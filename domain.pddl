(define (domain quest)
    (:requirements :strips :typing)
    (:types knight door key location)
    (:predicates
        (at ?k - knight ?l - location)
        (has ?k - knight ?i - key)
        (locked ?d - door))
    (:action unlock-door
        :parameters (?k1 - key)
        :precondition (and (has ?k ?k1) (locked ?d))
        :effect (and (unlocked ?d) (not (locked ?d)))
    )
    (:action move
        :parameters (?l1 - location ?l2 - location)
        :precondition (and true)
        :effect (and (connected ?l1 ?l2))
    )
    )
