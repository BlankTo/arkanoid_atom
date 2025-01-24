from utils import equal_collections
from core.events import event_pool

class Object:

    def __init__(self, frames_id, sequence, current_properties= None, unexplained= {}, explained_unexplained= {}, events= {}, rules= []):

        self.frames_id = frames_id[:]

        self.sequence = sequence[:]

        if current_properties is None: self.current_properties = sequence[-1].properties
        else: self.current_properties = current_properties

        self.unexplained = {fid: [ex.copy() for ex in v_list] for fid, v_list in unexplained.items()}

        self.explained_unexplained = {fid: [ex.copy() for ex in v_list] for fid, v_list in explained_unexplained.items()}

        self.events = {fid: [ex.copy() for ex in v_list] for fid, v_list in events.items()}

        self.rules = rules[:]

        self.prediction = self.compute_next(frames_id[-1])

    def copy(self):
        return Object(self.frames_id, self.sequence, self.current_properties, self.unexplained, self.explained_unexplained, self.events, self.rules)

    def compute_next(self, frame_id):

        new_properties = {property_class: value for property_class, value in self.current_properties.items()}

        for rule in self.rules:
            triggered, effects, offset = rule.trigger(self, frame_id - rule.cause_offset)
            if triggered:
                for effect in effects:
                    p_class = effect.property_class
                    if p_class not in new_properties.keys(): new_properties[p_class] = 0
                    new_properties[p_class] = effect.a * new_properties[p_class] + effect.b

        new_new_properties = {property_class: value for property_class, value in new_properties.items()}

        #for property_class in self.current_properties.keys():
        #    for prop_to_modify, change in property_class.effects(self.current_properties).items():
        #        new_properties[prop_to_modify] += change

        for property_class in new_properties.keys():
            for prop_to_modify, change in property_class.effects(new_properties).items():
                new_new_properties[prop_to_modify] += change

        return new_new_properties
    
    def update(self, frame_id, patch, new_properties, other_patches):

        self.frames_id.append(frame_id)
        self.sequence.append(patch)
        self.current_properties = new_properties

        previous_patch = self.sequence[-2]
        current_patch = self.sequence[-1]

        new_events = []
        for event in event_pool:
            if event.check(previous_patch, current_patch, other_patches):
                new_events.append(event)
        self.events[frame_id] = new_events

        self.prediction = self.compute_next(frame_id)

    def add_unexplained(self, unexplained_dict):
        for frame_id, unexplained in unexplained_dict.items():
            if frame_id in self.unexplained.keys(): self.unexplained[frame_id].extend([ex.copy() for ex in unexplained])
            else: self.unexplained[frame_id] = [ex.copy() for ex in unexplained]

    def explain(self, frame_id, explained):

        to_explain = []
        for unexpl in self.unexplained[frame_id]:
            if any([expl.test(unexpl) for expl in explained]):
                to_explain.append(unexpl)
        
        for unexpl in to_explain:
            self.unexplained[frame_id].remove(unexpl)
            if len(self.unexplained[frame_id]) == 0: self.unexplained.pop(frame_id)
            if frame_id in self.explained_unexplained.keys(): self.explained_unexplained[frame_id].append(unexpl)
            else: self.explained_unexplained[frame_id] = [unexpl]

    def check_and_explain(self, frame_id, explained):

        check = [False for _ in explained]

        unexplained_to_explain = []
        if frame_id in self.unexplained.keys():
            for unexpl in self.unexplained[frame_id]:
                for expl_idx, expl in enumerate(explained):
                    if expl.test(unexpl):
                        unexplained_to_explain.append(unexpl)
                        check[expl_idx] = True # si potrebbe controllare che ogni expl spieghi un solo unexplained, ma servono altri cambiamenti prima
                        break

        already_explained = []
        if frame_id in self.explained_unexplained.keys():
            for expl_unexpl in self.explained_unexplained[frame_id]:
                for expl_idx, expl in enumerate(explained):
                    if expl.test(expl_unexpl):
                        already_explained.append(expl_unexpl)
                        check[expl_idx] = True
                        break

        if all(check) and check:
        
            for unexpl in unexplained_to_explain:
                self.unexplained[frame_id].remove(unexpl)
                if len(self.unexplained[frame_id]) == 0: self.unexplained.pop(frame_id)
                if frame_id in self.explained_unexplained.keys(): self.explained_unexplained[frame_id].append(unexpl)
                else: self.explained_unexplained[frame_id] = [unexpl]

            return True

        else: return False

    def add_rule(self, rule): self.rules.append(rule)

    def __eq__(self, other):
        
        if isinstance(other, Object):
            if set(self.frames_id) != set(other.frames_id): return False
            if not equal_collections(self.sequence, other.sequence): return False
            if not equal_collections(self.unexplained, other.unexplained): return False
            if not equal_collections(self.explained_unexplained, other.explained_unexplained): return False
            if not equal_collections(self.events, other.events): return False
            if not equal_collections(self.rules, other.rules): return False
            return True

    def __repr__(self):
        ss = f'[{self.sequence[0].description}'
        for patch in self.sequence[1:]:
            ss += f', {patch.description}'
        ss += '] -> {'
        for prop_class, val in self.current_properties.items():
            ss += f'({prop_class.name()}: {val})'
        ss += '} - unexpl: {'
        for frame_id, unexpl in self.unexplained.items():
            ss += f'{frame_id}: {unexpl} |'
        ss += '} - expl: {'
        for frame_id, expl in self.explained_unexplained.items():
            ss += f'{frame_id}: {expl} |'
        ss += '} - events: {'
        for frame_id, ev in self.events.items():
            ss += f'{frame_id}: {ev} |'
        ss += '} - rules: {'
        for ruid, ru in enumerate(self.rules):
            ss += f'rule_{ruid}: {ru} |'
        ss += '}'
        return ss