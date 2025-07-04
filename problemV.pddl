(define (problem  whisperingforest-quest)
    (:domain whisperingforest)

    (:objects
        hero - hero
        forest-spirit - forest-spirit
        temple-guard - temple-guard
        crystal - crystal
        key - key
        village - village
        dark-warden - dark-warden
        temple - temple
        obstacle - obstacle
    )

    (:init
        (in Village Hero)
        (has-crystal Hero)
        (not (possessed Forest-Spirit Key))
        (in Temple Temple-Guard)
        (defeated Temple-Guard)
        (at Hero Village)
        (on Forest-Spirit Obstacle)
        (clear Temple)
    )

    (:goal
        (and
            (has-crystal Hero)
            (defeated Dark-Warden)
            (not (possessed Forest-Spirit Key))
            (in Village Hero)
        )
    )
)