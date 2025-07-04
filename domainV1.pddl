(define (domain dungeon-exploration)
    (:requirements :strips :typing)               ; PDDL requirements declaration

    (:types
        location character item - object           ; Basic object hierarchy
        village square forest cliff temple - location ; Specific location types
        hero elder monster spirit - character       ; Character types
        feather herbs rope dagger key - item        ; Item types
        gold - object                               ; Currency type
    )

    (:predicates
        (at ?obj - object ?loc - location)        ; Object/character is at a location
        (connected ?loc1 - location ?loc2 - location) ; Locations are connected
        (has-item ?char - character ?item - item) ; Character has an item
        (door-open ?from - location ?to - location) ; Door state between locations
        (monster-defeated ?m - monster)           ; Monster defeat status
        (quest-accepted)                          ; Quest has been accepted
        (feather-retrieved)                       ; Feather has been retrieved
        (treasure-found)                          ; Victory condition
        (gold-amount ?char - character ?amount - gold) ; Amount of gold a character has
    )

    (:action speak-to-elder
        :parameters (?h - hero ?e - elder ?loc - location)
        :precondition (and 
            (at ?h ?loc)                         ; Hero is at the elder's location
            (at ?e ?loc)                         ; Elder is at the same location
        )
        :effect (and 
            (quest-accepted)                     ; Quest to prove worth is accepted
        )
    )

    (:action gather-supplies
        :parameters (?h - hero ?loc - location)
        :precondition (at ?h ?loc)                ; Hero is at the market location
        :effect (and 
            ; Supplies can be gathered, but specific effects depend on choices made
        )
    )

    (:action buy-item
        :parameters (?h - hero ?item - item ?cost - gold ?loc - location)
        :precondition (and 
            (at ?h ?loc)                         ; Hero is at the market
            (gold-amount ?h ?amount)             ; Hero has a certain amount of gold
            (>= ?amount ?cost)                   ; Hero can afford the item
        )
        :effect (and 
            (has-item ?h ?item)                  ; Hero now has the item
            (not (gold-amount ?h ?amount))       ; Update gold amount after purchase
        )
    )

    (:action accept-quest
        :parameters (?h - hero ?e - elder)
        :precondition (and 
            (quest-accepted)                     ; Quest has been accepted
        )
        :effect (and 
            (feather-retrieved)                  ; Feather quest is now active
        )
    )

    (:action retrieve-feather
        :parameters (?h - hero ?loc - location)
        :precondition (and 
            (at ?h ?loc)                         ; Hero is at the cliff location
            (feather-retrieved)                  ; Quest to retrieve feather is active
        )
        :effect (and 
            (has-item ?h feather)                ; Hero retrieves the feather
        )
    )

    (:action enter-forest
        :parameters (?h - hero ?loc - location)
        :precondition (at ?h ?loc)                ; Hero is at the forest entrance
        :effect (and 
            (at ?h forest)                       ; Hero enters the forest
        )
    )

    (:action encounter-spirit
        :parameters (?h - hero ?s - spirit)
        :precondition (and 
            (at ?h forest)                       ; Hero is in the forest
            (at ?s forest)                       ; Spirit is present in the forest
        )
        :effect (and 
            ; Spirit interaction can lead to various outcomes
        )
    )

    (:action solve-riddle
        :parameters (?h - hero ?s - spirit ?answer - string)
        :precondition (and 
            (at ?h forest)                       ; Hero is in the forest
            (at ?s forest)                       ; Spirit is present
        )
        :effect (and 
            (if (equal ?answer "an echo")        ; Correct answer
                (treasure-found)                ; Hero finds the key
                (not (treasure-found))          ; Incorrect answer
            )
        )
    )

    (:action return-to-elder
        :parameters (?h - hero ?e - elder)
        :precondition (and 
            (has-item ?h feather)                ; Hero has the feather
            (at ?h village)                      ; Hero is at the village
            (at ?e village)                      ; Elder is at the village
        )
        :effect (and 
            (treasure-found)                     ; Quest is completed
        )
    )

    (:action enter-temple
        :parameters (?h - hero ?loc - location ?k - key)
        :precondition (and 
            (at ?h ?loc)                         ; Hero is at the temple
            (has-item ?h ?k)                     ; Hero has the key
        )
        :effect (and 
            (at ?h temple)                       ; Hero enters the temple
        )
    )

    (:action fight-dark-warden
        :parameters (?h - hero ?m - monster)
        :precondition (and 
            (at ?h temple)                       ; Hero is in the temple
            (at ?m temple)                       ; Dark Warden is present
        )
        :effect (and 
            (monster-defeated ?m)                ; Dark Warden is defeated
            (treasure-found)                     ; Hero finds the Crystal of Light
        )
    )

    (:action negotiate-with-dark-warden
        :parameters (?h - hero ?m - monster)
        :precondition (and 
            (at ?h temple)                       ; Hero is in the temple
            (at ?m temple)                       ; Dark Warden is present
        )
        :effect (and 
            ; Negotiation can lead to various outcomes
        )
    )
)