"""Use-case layer: owns decisions (get-or-404, authorization, conflicts).

Routes stay thin (parse → call service → return); trivial list reads may hit the
repository directly from the route.
"""
