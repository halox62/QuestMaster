```pddl
(define (domain wizard-quest)
(:requirements :strips :typing)
(:types wizard spell location entity trial)
(:predicates
    (at ?w - wizard ?l - location)
    (has_spell ?w - wizard ?s - spell)
    (arcane_lock ?l - location)
    (spell_learned ?w - wizard)
    (gate_open ?l - location)
    (guardian_summoned ?l - location)
    (castle_vanished ?l - location)
    (trial_completed ?w - wizard ?t - trial))
(:action learn-spell-from-spirits
    :parameters (?w - wizard ?s - spell ?l - location)
    :precondition (and (at ?w ?l))
    :effect (and (has_spell ?w ?s) (spell_learned ?w))
)
(:action learn-spell-from-ruins
    :parameters (?w - wizard ?s - spell ?l - location)
    :precondition (and (at ?w ?l))
    :effect (and (has_spell ?w ?s) (spell_learned ?w))
)
(:action cast-correct-spell
    :parameters (?w - wizard ?s - spell ?l - location)
    :precondition (and (has_spell ?w ?s) (arcane_lock ?l) (spell_learned ?w))
    :effect (and (gate_open ?l) (not (arcane_lock ?l)))
)
(:action cast-wrong-spell
    :parameters (?w - wizard ?s - spell ?l - location)
    :precondition (and (has_spell ?w ?s) (arcane_lock ?l) (spell_learned ?w))
    :effect (and (guardian_summoned ?l) (not (arcane_lock ?l)))
)
(:action enter-castle
    :parameters (?w - wizard ?l - location)
    :precondition (and (gate_open ?l) (at ?w ?l))
    :effect (and (not (at ?w ?l)) (at ?w ?l))
)
(:action complete-trial
    :parameters (?w - wizard ?t - trial ?l - location)
    :precondition (and (at ?w ?l))
    :effect (and (trial_completed ?w ?t))
)
)
```