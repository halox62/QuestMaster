```pddl
(define (problem wizard-quest-to-castle)
(:domain wizard-quest)
(:objects
    wizard1 - wizard
    spell1 - spell
    whispering-forest - location
    castle-gates - location
    castle-interior - location
    trial1 - trial
    trial2 - trial)
(:init
    (at wizard1 whispering-forest)
    (arcane_lock castle-gates))
(:goal
    (and (trial_completed wizard1 trial1) (trial_completed wizard1 trial2)))
)
```