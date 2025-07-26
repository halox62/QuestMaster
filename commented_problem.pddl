(define (problem brava-island-treasure-quest)
  (:domain brava-island-adventure)
  (:objects
    adventurer - player                      ; the player character named adventurer
    island_shore jungle_edge collapsed_cave native_village temple_entrance - location  ; various locations on the island
    sacred_medallion - item                  ; the key item to find
    native_ally - ally                       ; an ally character native to the island
    simple_trap - trap                       ; a trap present in the environment
    altar_puzzle - puzzle)                   ; a puzzle to solve at the altar
  (:init
    (player-at adventurer island_shore)     ; adventurer starts at the island shore
    (at-shore)                              ; player is currently at the shore location
    (not (at-jungle-edge))                  ; player is not at the jungle edge initially
    (not (at-collapsed-cave))               ; player is not at the collapsed cave initially
    (not (at-village))                      ; player is not at the native village initially
    (not (temple-accessible))               ; temple is initially inaccessible
    (not (medallion-found))                 ; medallion has not been found yet
    (not (native-trust-earned))             ; trust of native ally not yet earned
    (not (puzzle-solved))                   ; altar puzzle not solved yet
    (not (treasure-claimed))                ; treasure has not been claimed yet
    (not (wounded adventurer))              ; adventurer is not wounded at start
    (not (ally-present native_ally island_shore)) ; native ally not present at island shore
    (not (ally-present native_ally jungle_edge))  ; native ally not present at jungle edge
    (not (ally-present native_ally collapsed_cave)) ; native ally not present at collapsed cave
    (not (ally-present native_ally native_village)) ; native ally not present at native village
    (not (trap-active simple_trap jungle_edge)) ; trap is not active at jungle edge
    (not (trap-triggered simple_trap jungle_edge)) ; trap has not been triggered at jungle edge
    (not (lost-in-jungle))                  ; player is not lost in the jungle
    (not (fatally-injured adventurer))     ; adventurer is not fatally injured
    (not (trapped adventurer)))             ; adventurer is not trapped
  (:goal
    (and (treasure-claimed))))               ; goal is to have claimed the treasure