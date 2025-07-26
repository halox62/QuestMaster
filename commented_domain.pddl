(define (domain brava-island-adventure) ; define the domain named brava-island-adventure
  (:requirements :strips :typing) ; specify requirements: STRIPS and typing support
  (:types player location item trap puzzle ally) ; define types used in the domain
  (:predicates
    (player-at ?p - player ?l - location) ; player ?p is at location ?l
    (has ?p - player ?i - item) ; player ?p has item ?i
    (ally-present ?a - ally ?l - location) ; ally ?a is present at location ?l
    (wounded ?p - player) ; player ?p is wounded
    (medallion-found) ; medallion has been found
    (native-trust-earned) ; trust of natives has been earned
    (puzzle-solved) ; puzzle has been solved
    (treasure-claimed) ; treasure has been claimed
    (temple-accessible) ; temple is accessible
    (trap-active ?t - trap ?l - location) ; trap ?t is active at location ?l
    (trap-triggered ?t - trap ?l - location) ; trap ?t has been triggered at location ?l
    (at-jungle-edge) ; player is at the jungle edge
    (at-shore) ; player is at the shore
    (at-village) ; player is at the village
    (at-collapsed-cave) ; player is at the collapsed cave
    (lost-in-jungle) ; player is lost in the jungle
    (fatally-injured ?p - player) ; player ?p is fatally injured
    (trapped ?p - player) ; player ?p is trapped
  )
  (:action venture-into-dense-jungle
    :parameters (?p - player ?shore - location ?jungle_edge - location) ; parameters: player, shore location, jungle edge location
    :precondition (and (player-at ?p ?shore) (at-shore)) ; player at shore and at-shore condition true
    :effect (and (not (player-at ?p ?shore)) (player-at ?p ?jungle_edge) (not (at-shore)) (at-jungle-edge)) ; move player from shore to jungle edge, update location flags
  )
  (:action scout-along-shoreline
    :parameters (?p - player ?shore - location ?jungle_edge - location) ; parameters: player, shore, jungle edge
    :precondition (and (player-at ?p ?shore) (at-shore) (not (wounded ?p))) ; player at shore, not wounded
    :effect (and (not (player-at ?p ?shore)) (player-at ?p ?jungle_edge) (not (at-shore)) (at-jungle-edge) (not (wounded ?p))) ; move player to jungle edge, remain not wounded
  )
  (:action rest-and-prepare-supplies
    :parameters (?p - player ?shore - location) ; parameters: player, shore
    :precondition (and (player-at ?p ?shore) (at-shore) (not (wounded ?p))) ; player at shore, not wounded
    :effect (and (player-at ?p ?shore) (at-shore) (not (wounded ?p))) ; player remains at shore, not wounded (resting)
  )
  (:action call-out-for-natives
    :parameters (?p - player ?shore - location ?native - ally) ; parameters: player, shore, native ally
    :precondition (and (player-at ?p ?shore) (at-shore) (not (ally-present ?native ?shore))) ; player at shore, native not present
    :effect (and (ally-present ?native ?shore)) ; native ally becomes present at shore
  )
  (:action proceed-cautiously-to-collapsed-cave
    :parameters (?p - player ?jungle_edge - location ?cave - location) ; parameters: player, jungle edge, cave
    :precondition (and (player-at ?p ?jungle_edge) (at-jungle-edge)) ; player at jungle edge
    :effect (and (not (player-at ?p ?jungle_edge)) (player-at ?p ?cave) (not (at-jungle-edge)) (at-collapsed-cave)) ; move player to collapsed cave, update location flags
  )
  (:action explore-jungle-outskirts-for-allies
    :parameters (?p - player ?jungle_edge - location ?native - ally) ; parameters: player, jungle edge, native ally
    :precondition (and (player-at ?p ?jungle_edge) (at-jungle-edge)) ; player at jungle edge
    :effect (and (ally-present ?native ?jungle_edge)) ; native ally becomes present at jungle edge
  )
  (:action set-simple-traps
    :parameters (?p - player ?jungle_edge - location ?trap - trap) ; parameters: player, jungle edge, trap
    :precondition (and (player-at ?p ?jungle_edge) (at-jungle-edge) (not (wounded ?p))) ; player at jungle edge, not wounded
    :effect (and (trap-active ?trap ?jungle_edge) (not (wounded ?p))) ; activate trap at jungle edge, player remains not wounded
  )
  (:action head-into-jungle-to-collapsed-cave
    :parameters (?p - player ?jungle_edge - location ?cave - location) ; parameters: player, jungle edge, cave
    :precondition (and (player-at ?p ?jungle_edge) (at-jungle-edge)) ; player at jungle edge
    :effect (and (not (player-at ?p ?jungle_edge)) (player-at ?p ?cave) (not (at-jungle-edge)) (at-collapsed-cave)) ; move player to collapsed cave, update location flags
  )
  (:action follow-smoke-to-village
    :parameters (?p - player ?jungle_edge - location ?village - location) ; parameters: player, jungle edge, village
    :precondition (and (player-at ?p ?jungle_edge) (at-jungle-edge)) ; player at jungle edge
    :effect (and (not (player-at ?p ?jungle_edge)) (player-at ?p ?village) (not (at-jungle-edge)) (at-village)) ; move player to village, update location flags
  )
  (:action set-up-temporary-camp
    :parameters (?p - player ?jungle_edge - location) ; parameters: player, jungle edge
    :precondition (and (player-at ?p ?jungle_edge) (at-jungle-edge) (not (wounded ?p))) ; player at jungle edge, not wounded
    :effect (and (player-at ?p ?jungle_edge) (at-jungle-edge) (not (wounded ?p))) ; player remains at jungle edge, not wounded (camping)
  )
  (:action search-carefully-for-medallion
    :parameters (?p - player ?cave - location ?medallion - item) ; parameters: player, cave, medallion item
    :precondition (and (player-at ?p ?cave) (at-collapsed-cave) (not (wounded ?p))) ; player at cave, not wounded
    :effect (and (medallion-found) (has ?p ?medallion)) ; medallion found and player has it
  )
  (:action rush-through-cave-and-get-wounded
    :parameters (?p - player ?cave - location ?trap - trap) ; parameters: player, cave, trap
    :precondition (and (player-at ?p ?cave) (at-collapsed-cave) (not (wounded ?p))) ; player at cave, not wounded
    :effect (and (wounded ?p) (trap-triggered ?trap ?cave)) ; player becomes wounded, trap triggered at cave
  )
  (:action retreat-to-jungle-edge
    :parameters (?p - player ?cave - location ?jungle_edge - location) ; parameters: player, cave, jungle edge
    :precondition (and (player-at ?p ?cave) (at-collapsed-cave)) ; player at cave
    :effect (and (not (player-at ?p ?cave)) (player-at ?p ?jungle_edge) (not (at-collapsed-cave)) (at-jungle-edge)) ; move player back to jungle edge, update location flags
  )
  (:action enter-cave-with-ally
    :parameters (?p - player ?native - ally ?cave - location) ; parameters: player, native ally, cave
    :precondition (and (player-at ?p ?cave) (ally-present ?native ?cave) (at-collapsed-cave) (not (medallion-found))) ; player and ally at cave, medallion not found
    :effect (and) ; no effect specified (placeholder)
  )
  (:action take-medallion-and-go-to-village-with-ally
    :parameters (?p - player ?native - ally ?cave - location ?village - location ?medallion - item) ; parameters: player, native ally, cave, village, medallion
    :precondition (and (player-at ?p ?cave) (ally-present ?native ?cave) (at-collapsed-cave) (not (medallion-found))) ; player and ally at cave, medallion not found
    :effect (and (medallion-found) (has ?p ?medallion) (not (player-at ?p ?cave)) (player-at ?p ?village) (ally-present ?native ?village) (not (at-collapsed-cave)) (at-village) (native-trust-earned)) ; player obtains medallion, moves to village with ally, trust earned
  )
  (:action explore-jungle-outskirts-with-ally
    :parameters (?p - player ?native - ally ?jungle_edge - location) ; parameters: player, native ally, jungle edge
    :precondition (and (player-at ?p ?jungle_edge) (ally-present ?native ?jungle_edge) (at-jungle-edge) (not (wounded ?p))) ; player and ally at jungle edge, player not wounded
    :effect (and) ; no effect specified (placeholder)
  )
  (:action gain-ally-trust-with-gift
    :parameters (?p - player ?native - ally ?shore - location) ; parameters: player, native ally, shore
    :precondition (and (player-at ?p ?shore) (at-shore) (not (ally-present ?native ?shore))) ; player at shore, native not present
    :effect (and (ally-present ?native ?shore)) ; native ally becomes present at shore (trust gained)
  )
  (:action insist-on-alone
    :parameters (?p - player ?native - ally ?shore - location ?jungle_edge - location) ; parameters: player, native ally, shore, jungle edge
    :precondition (and (player-at ?p ?shore) (at-shore) (not (ally-present ?native ?shore))) ; player at shore, native not present
    :effect (and (not (ally-present ?native ?shore)) (not (player-at ?p ?shore)) (player-at ?p ?jungle_edge) (not (at-shore)) (at-jungle-edge)) ; player moves alone from shore to jungle edge, native not present
  )
  (:action ask-native-for-guidance
    :parameters (?p - player ?native - ally ?shore - location ?jungle_edge - location) ; parameters: player, native ally, shore, jungle edge
    :precondition (and (player-at ?p ?shore) (ally-present ?native ?shore) (at-shore)) ; player and native at shore
    :effect (and (not (player-at ?p ?shore)) (player-at ?p ?jungle_edge) (not (at-shore)) (at-jungle-edge)) ; player moves to jungle edge with native's guidance
  )
  (:action visit-village-to-earn-trust
    :parameters (?p - player ?village - location) ; parameters: player, village
    :precondition (and (player-at ?p ?village) (at-village) (not (native-trust-earned)) (medallion-found)) ; player at village, medallion found, trust not yet earned
    :effect (and (native-trust-earned)) ; trust of natives earned
  )
  (:action attempt-negotiate-without-medallion
    :parameters (?p - player ?village - location) ; parameters: player, village
    :precondition (and (player-at ?p ?village) (at-village) (not (medallion-found))) ; player at village without medallion
    :effect (and (wounded ?p) (fatally-injured ?p)) ; player becomes wounded and fatally injured (failed negotiation)
  )
  (:action leave-village-to-find-medallion
    :parameters (?p - player ?village - location ?cave - location) ; parameters: player, village, cave
    :precondition (and (player-at ?p ?village) (at-village) (not (medallion-found))) ; player at village without medallion
    :effect (and (not (player-at ?p ?village)) (player-at ?p ?cave) (not (at-village)) (at-collapsed-cave)) ; player moves from village to collapsed cave
  )
  (:action rest-at-jungle-edge
    :parameters (?p - player ?jungle_edge - location) ; parameters: player, jungle edge
    :precondition (and (player-at ?p ?jungle_edge) (at-jungle-edge) (wounded ?p)) ; player at jungle edge and wounded
    :effect (and (not (wounded ?p))) ; player heals and is no longer wounded
  )
  (:action travel-to-village-with-medallion
    :parameters (?p - player ?jungle_edge - location ?village - location ?medallion - item) ; parameters: player, jungle edge, village, medallion
    :precondition (and (player-at ?p ?jungle_edge) (at-jungle-edge) (medallion-found) (has ?p ?medallion)) ; player at jungle edge with medallion
    :effect (and (not (player-at ?p ?jungle_edge)) (player-at ?p ?village) (not (at-jungle-edge)) (at-village)) ; player moves to village
  )
  (:action explore-jungle-outskirts-with-medallion
    :parameters (?p - player ?native - ally ?jungle_edge - location ?medallion - item) ; parameters: player, native ally, jungle edge, medallion
    :precondition (and (player-at ?p ?jungle_edge) (ally-present ?native ?jungle_edge) (at-jungle-edge) (medallion-found) (has ?p ?medallion)) ; player and ally at jungle edge with medallion
    :effect (and) ; no effect specified (placeholder)
  )
  (:action earn-native-trust-at-village
    :parameters (?p - player ?village - location) ; parameters: player, village
    :precondition (and (player-at ?p ?village) (at-village) (medallion-found) (not (native-trust-earned))) ; player at village with medallion, trust not earned
    :effect (and (native-trust-earned)) ; trust earned
  )
  (:action journey-to-temple-entrance
    :parameters (?p - player ?village - location ?temple - location) ; parameters: player, village, temple
    :precondition (and (player-at ?p ?village) (at-village) (native-trust-earned)) ; player at village with trust earned
    :effect (and (not (player-at ?p ?village)) (player-at ?p ?temple) (not (at-village)) (temple-accessible)) ; player moves to temple, temple becomes accessible
  )
  (:action learn-altar-puzzle
    :parameters (?p - player ?village - location ?puzzle - puzzle) ; parameters: player, village, puzzle
    :precondition (and (player-at ?p ?village) (at-village) (native-trust-earned)) ; player at village with trust earned
    :effect (and (puzzle-solved)) ; puzzle is solved
  )
  (:action rest-before-final-leg
    :parameters (?p - player ?village - location) ; parameters: player, village
    :precondition (and (player-at ?p ?village) (at-village) (not (wounded ?p))) ; player at village, not wounded
    :effect (and) ; no effect specified (placeholder)
  )
  (:action attempt-solve-altar-puzzle
    :parameters (?p - player ?temple - location ?puzzle - puzzle) ; parameters: player, temple, puzzle
    :precondition (and (player-at ?p ?temple) (temple-accessible)) ; player at accessible temple
    :effect (and (puzzle-solved)) ; puzzle is solved
  )
  (:action search-temple-for-hints
    :parameters (?p - player ?temple - location) ; parameters: player, temple
    :precondition (and (player-at ?p ?temple) (temple-accessible) (not (wounded ?p))) ; player at accessible temple, not wounded
    :effect (and) ; no effect specified (placeholder)
  )
  (:action enter-treasure-vault
    :parameters (?p - player ?temple - location) ; parameters: player, temple
    :precondition (and (player-at ?p ?temple) (temple-accessible) (puzzle-solved)) ; player at accessible temple with puzzle solved
    :effect (and (treasure-claimed)) ; treasure is claimed
  )
  (:action inspect-treasure-for-traps
    :parameters (?p - player ?temple - location) ; parameters: player, temple
    :precondition (and (player-at ?p ?temple) (temple-accessible) (not (wounded ?p))) ; player at accessible temple, not wounded
    :effect (and) ; no effect specified (placeholder)
  )
  (:action take-treasure-and-leave
    :parameters (?p - player ?temple - location) ; parameters: player, temple
    :precondition (and (player-at ?p ?temple) (temple-accessible) (puzzle-solved) (treasure-claimed)) ; player at accessible temple with puzzle solved and treasure claimed
    :effect (and) ; no effect specified (placeholder)
  )
  (:action push-forward-to-find-medallion-wounded
    :parameters (?p - player ?cave - location ?medallion - item) ; parameters: player, cave, medallion
    :precondition (and (player-at ?p ?cave) (at-collapsed-cave) (wounded ?p)) ; player at cave and wounded
    :effect (and (medallion-found) (has ?p ?medallion)) ; medallion found and player has it despite being wounded
  )
  (:action retreat-to-jungle-edge-to-heal
    :parameters (?p - player ?cave - location ?jungle_edge - location) ; parameters: player, cave, jungle edge
    :precondition (and (player-at ?p ?cave) (at-collapsed-cave) (wounded ?p)) ; player at cave and wounded
    :effect (and (not (wounded ?p)) (not (player-at ?p ?cave)) (player-at ?p ?jungle_edge) (not (at-collapsed-cave)) (at-jungle-edge)) ; player moves to jungle edge and heals
  )
  (:action attempt-call-for-help-while-wounded
    :parameters (?p - player ?native - ally ?cave - location) ; parameters: player, native ally, cave
    :precondition (and (player-at ?p ?cave) (at-collapsed-cave) (wounded ?p) (not (ally-present ?native ?cave))) ; player wounded at cave, native not present
    :effect (and (fatally-injured ?p)) ; player becomes fatally injured (failed help)
  )
)