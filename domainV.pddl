(define (domain whisperingforest)
    (:requirements :strips :typing)

    (:types
        hero
        forest-spirit
        temple-guard
        crystal
        key
        village
        dark-warden
        temple
        obstacle
    )

    (:predicates
        (at ?x - hero ?y - location)
        (has-crystal ?x - hero)
        (has-key ?x - hero)
        (is-worthy ?x - hero)
        (in Temple ?x - hero)
        (defeated ?x - temple-guard)
        (possessed ?x - forest-spirit ?key - key)
        (at ?forest-spirit - forest-spirit ?tree - obstacle)
    )

    (:action pick-up-key
        :parameters (?x - hero)
        :precondition (and (in Village ?x) (not (has-key ?x)) (is-worthy ?x))
        :effect (and (has-key ?x) (not (defeated Temple)))
    )

    (:action talk-to-spirit
        :parameters (?x - hero)
        :precondition (and (at ?x - forest-spirit Village))
        :effect (and (possessed ?x Forest-Spirit) (not (defeated Temple))))
    )

    (:action enter-temple
        :parameters (?x - hero)
        :precondition (and (has-key ?x) (in Temple ?x))
        :effect (and (in Temple ?x) (not (defeated Temple))))
    )

    (:action fight-dark-warden
        :parameters (?x - hero)
        :precondition (and (in Temple ?x) (defeated Temple)))
        (; This line declares the predicate 'on'---.
        :effect (and (has-crystal ?x) (not (defeated Dark-Warden))))
    )

    (:action exit-temple
        :parameters (?x - hero)
        :precondition (in Temple ?x)
        :effect (and (not (in Temple ?x)) (not (defeated Temple))))
    )

    (:action search-for-crystal
        :parameters (?x - hero)
        :precondition (has-crystal ?x)
        :effect (and (has-crystal ?x) (not (in Village ?x))))
    )

    (:action return-to-village
        :parameters (?x - hero)
        :precondition (search-for-crystal ?x)
        :effect (and (in Village ?x) (not (has-crystal ?x))))
    )

    (:action possess-key
        :parameters (?x - forest-spirit)
        :precondition (possessed ?x Key)
        :effect (and (not (defeated Temple)) (not (in Temple ?x))))
    )

    (:action return-key
        :parameters (?x - hero)
        :precondition (has-key ?x)
        :effect (and (not (has-key ?x)) (in Village ?x)))
)

