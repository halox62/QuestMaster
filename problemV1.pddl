(define (problem dawnmere-quest)
    (:domain dungeon-exploration)                ; References the dungeon-exploration domain

    (:objects
        hero - character                          ; The main character (hero)
        elder - character                         ; The village elder
        goblin orc - monster                      ; Enemies in the quest
        whispering-forest - location              ; The forest location
        village-square - location                 ; The village square
        cliffs - location                         ; Cliffs of Echoing Winds
        temple - location                         ; Temple of Echoes
        feather - item                           ; The feather to retrieve
        healing-herbs rope dagger - item         ; Items available for purchase
        crystal - item                           ; The Crystal of Light
        golden-key - key                         ; The key to the temple
        gold - object                             ; Currency for transactions
    )

    (:init
        ; Initial character positions
        (at hero village-square)                  ; Hero starts in the village square
        (at elder village-square)                 ; Elder is in the village square
        (at goblin whispering-forest)             ; Goblin is in the forest
        (at orc temple)                          ; Orc is guarding the temple
        
        ; Initial item locations
        (at feather cliffs)                       ; Feather is at the cliffs
        (at healing-herbs village-square)         ; Healing herbs available in the village
        (at rope village-square)                  ; Rope available in the village
        (at dagger village-square)                ; Dagger available in the village
        (at golden-key whispering-forest)         ; Key is hidden in the forest
        
        ; Initial gold amount for the hero
        (gold-amount hero 10)                    ; Hero starts with 10 gold
        
        ; Room connections
        (connected village-square whispering-forest) ; Village connects to the forest
        (connected whispering-forest cliffs)      ; Forest connects to the cliffs
        (connected cliffs temple)                  ; Cliffs connect to the temple
        
        ; Initial quest state
        (not (quest-accepted))                    ; Quest has not been accepted yet
        (not (feather-retrieved))                 ; Feather has not been retrieved yet
        (not (treasure-found))                     ; Treasure has not been found yet
    )

    (:goal
        (and 
            (treasure-found)                      ; Main goal: find the Crystal of Light
            (monster-defeated goblin)             ; Defeat the goblin
            (monster-defeated orc)                ; Defeat the orc
            (at hero temple)                       ; Hero reaches the temple
        )
    )
)