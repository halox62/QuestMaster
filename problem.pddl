(define (problem maghi-quest)
    (:domain maghi)
    (:objects
        mago - magician
        incantesimo - spell
        castello - castle
        village - location)
    (:init
        (knows mago incantesimo)
        (at mago village)
        (locked castello))
    (:goal
        (and (knows incantesimo) (at castello)))
    )
