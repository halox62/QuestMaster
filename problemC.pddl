(define (problem brava-island-treasure-quest)
(:domain brava-island-adventure)
(:objects
    adventurer - player
    shore - location
    jungle-edge - location
    collapsed-cave - location
    village - location
    temple - location
    medallion - item
    obsidian-medallion - item
    venomous-trap - trap
    altar-puzzle - puzzle
    native-ally - ally)
(:init
    (player-at adventurer shore)
    (trap-active venomous-trap jungle-edge)
    (puzzle-active altar-puzzle temple))
(:goal
    (and (treasure-claimed adventurer)))
)
