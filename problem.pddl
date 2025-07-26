(define (problem brava-island-treasure-quest)
  (:domain brava-island-adventure)
  (:objects
    adventurer - player
    island_shore jungle_edge collapsed_cave native_village temple_entrance - location
    sacred_medallion - item
    native_ally - ally
    simple_trap - trap
    altar_puzzle - puzzle)
  (:init
    (player-at adventurer island_shore)
    (at-shore)
    (not (at-jungle-edge))
    (not (at-collapsed-cave))
    (not (at-village))
    (not (temple-accessible))
    (not (medallion-found))
    (not (native-trust-earned))
    (not (puzzle-solved))
    (not (treasure-claimed))
    (not (wounded adventurer))
    (not (ally-present native_ally island_shore))
    (not (ally-present native_ally jungle_edge))
    (not (ally-present native_ally collapsed_cave))
    (not (ally-present native_ally native_village))
    (not (trap-active simple_trap jungle_edge))
    (not (trap-triggered simple_trap jungle_edge))
    (not (lost-in-jungle))
    (not (fatally-injured adventurer))
    (not (trapped adventurer)))
  (:goal
    (and (treasure-claimed))))