(define (problem find-hidden-treasure)
  (:domain island-adventure)
  (:objects
    adventurer1 - adventurer
    shore jungle ruins treasure-chamber - location
    key1 - object
    jaguar - creature
  )
  (:init
    (at adventurer1 shore)
    (accessible shore)
    (accessible jungle)
    (creature-at jaguar jungle)
    (object-at key1 ruins)
    (path-revealed ruins)
    (puzzle-solved ruins)
  )
  (:goal
    (and (at adventurer1 treasure-chamber))
  )
)