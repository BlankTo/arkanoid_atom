from utils.various import equal_collections
from core.unexplained import (
    UnexplainedSpecificChange,
    UnexplainedNumericalChange,
    SpecificUnexplainedPhenomenon,
    NumericalUnexplainedPhenomenon,
    EventPhenomenon
    )
from core.events import Event

RULE_MIN_TIMES = 1
CAUSE_EFFECT_MAX_OFFSET = 3

class Rule:

    def __init__(self, cause_offset, causes, effects):
        self.cause_offset = cause_offset  # Difference between effect frame and cause frame
        self.causes = causes[:]           # List of generalized causes as phenomenons
        self.effects = effects[:]         # List of effects as phenomenons

    def trigger(self, obj, frame_id, debug= False):
        possible_causes = []
        possible_causes += obj.unexplained[frame_id] if frame_id in obj.unexplained.keys() else []
        possible_causes += obj.explained_unexplained[frame_id] if frame_id in obj.explained_unexplained.keys() else []
        possible_causes += obj.events[frame_id] if frame_id in obj.events.keys() else []
        if debug:
            for cause in self.causes:
                for pc in possible_causes:
                    print(f'{cause}.test({pc}) -> {cause.test(pc)}')
        if all([any([cause.test(pc) for pc in possible_causes]) for cause in self.causes]):
            return True, self.effects, self.cause_offset
        else: return False, None, None

    def __eq__(self, other):
        if not (isinstance(other, Rule)): return False
        if self.cause_offset != other.cause_offset: return False
        if not equal_collections(self.causes, other.causes): return False
        if not equal_collections(self.effects, other.effects): return False
        return True
    
    def my_hash(self):
        ss = f'{self.cause_offset}'
        for cause_hash in sorted([cause.my_hash() for cause in self.causes]):
            ss += cause_hash
        for effect_hash in sorted([effect.my_hash() for effect in self.effects]):
            ss += effect_hash
        return ss

    def __repr__(self):
        return f'rule\nwith causes: {self.causes}\nwith effects: {self.effects}\nafter {self.cause_offset} frames'

A_RANGE = [-1, 0, 1, 2, -2]#, 3, -3, 4, -4, 5, -5, 6, -6]
B_RANGE = [-1, 0, 1]

def convert_to_phenomenon(event_or_unexplained):

    if isinstance(event_or_unexplained, UnexplainedSpecificChange):
        return [SpecificUnexplainedPhenomenon({'unexplained_class': event_or_unexplained.__class__})]
    elif isinstance(event_or_unexplained, UnexplainedNumericalChange):
        previous = event_or_unexplained.previous_value
        final = event_or_unexplained.final_value
        if previous == 0:
            a = 0
            b = final
        else:
            a, b = divmod(final, previous)
        return [NumericalUnexplainedPhenomenon({'a': a, 'b': b, 'property_class': event_or_unexplained.property_class})]
    elif issubclass(event_or_unexplained, Event):
        return [EventPhenomenon({'event_class': event_or_unexplained}), EventPhenomenon({'event_class': event_or_unexplained.__base__})]
    else:
        print('nah2')
        exit(0)

def new_infer_rules(ind, present_objects, not_present_objects, frame_id, debug= False):

    explained_score = 0

    seen_rules = []

    all_ind_objs = {obj_id: present_objects[obj_id] if obj_id in present_objects.keys() else not_present_objects[obj_id] for obj_id in ind}

    for obj in all_ind_objs.values():

        obj.reset_explained_and_rules()

        obj_cause_effect_offset_times = {}
        obj_cause_effect_offset_rule = {}
        obj_cause_times = {}

        all_possible_causes = {}
        frames_with_possible_causes = []
        for ffid in range(0, frame_id + 1):
            all_possible_causes_ffid = []
            if ffid in obj.unexplained.keys(): all_possible_causes_ffid.extend(obj.unexplained[ffid])
            if ffid in obj.events.keys(): all_possible_causes_ffid.extend(obj.events[ffid])
            if all_possible_causes_ffid:
                all_possible_causes[ffid] = all_possible_causes_ffid
                frames_with_possible_causes.append(ffid)


        for cf in range(0, frame_id + 1):
            #print(f'cf: {cf}')

            if cf in frames_with_possible_causes:

                for ev in all_possible_causes[cf]:
                    causes = convert_to_phenomenon(ev)
                    for cause in causes:
                        cause_hash = cause.my_hash()
                        #print(f'\t\tcause: {cause_hash}')

                        if cause_hash in obj_cause_times.keys(): obj_cause_times[cause_hash] += 1
                        else: obj_cause_times[cause_hash] = 1

                        for ef in range(cf, cf + CAUSE_EFFECT_MAX_OFFSET if cf + CAUSE_EFFECT_MAX_OFFSET <= frame_id else frame_id + 1):
                            #print(f'\tef: {ef}')
                            offset = ef - cf

                            effects_set = obj.unexplained | obj.explained_unexplained
                            if ef in effects_set.keys():
                                for un in effects_set[ef]:
                                    effects = convert_to_phenomenon(un)
                                    for effect in effects:
                                        effect_hash = effect.my_hash()
                                        #print(f'\t\t\teffect: {effect}')
                                        if cause != effect:

                                            rule = Rule(offset, [cause], [effect])

                                            if (cause_hash, effect_hash, offset) in obj_cause_effect_offset_times.keys():
                                                obj_cause_effect_offset_times[((cause_hash, effect_hash, offset))] += 1
                                            else:
                                                obj_cause_effect_offset_times[((cause_hash, effect_hash, offset))] = 1
                                                obj_cause_effect_offset_rule[((cause_hash, effect_hash, offset))] = rule

        potential_rules = []
        cause_classes = []

        obj_explained_score = 0

        for (cause_hash, effect_hash, offset), times in obj_cause_effect_offset_times.items():
            if obj_cause_times[cause_hash] == times:
                obj_explained_score -= times
                rule = obj_cause_effect_offset_rule[((cause_hash, effect_hash, offset))]
                rule_hash = rule.my_hash()
                if rule_hash not in seen_rules: seen_rules.append(rule_hash)
                potential_rules.append(rule)
                if isinstance(rule.causes[0], EventPhenomenon): cause_classes.append(rule.causes[0].event_class)
                else: cause_classes.append(None)
        
        explained_score += obj_explained_score
        
        new_potential_rules = []
        for pr, cc in zip(potential_rules, cause_classes):
            if cc is not None:
                if cc.__base__ not in cause_classes: new_potential_rules.append(pr)

        for rule in new_potential_rules:
            obj.add_rule(rule)

    return explained_score, len(seen_rules)

        