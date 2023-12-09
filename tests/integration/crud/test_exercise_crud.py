import pytest
from gymhero.crud import exercise_crud, level_crud, bodypart_crud, exercise_type_crud
from gymhero.models.exercise import Exercise
from gymhero.schemas.exercise import ExerciseCreate, ExerciseInDB, ExerciseUpdate
from scripts.core._initsu import seed_superuser
from scripts.core.utils import _create_first_user
from sqlalchemy.exc import IntegrityError


def test_should_get_all_exercises(get_test_db, seed_test_database):
    exercises = exercise_crud.get_many(get_test_db)
    assert len(exercises) > 0 and [
        isinstance(exercise, Exercise) for exercise in exercises
    ]


def test_should_get_only_my_exercises(get_test_db, seed_test_database):
    # setup
    u = _create_first_user(
        get_test_db, "testing@testing.com", "testing", "Testing", False, True
    )
    n_to_change = 10
    exercises = exercise_crud.get_many(get_test_db, skip=0, limit=n_to_change)
    for exercise in exercises:
        exercise.owner_id = u.id
        get_test_db.add(exercise)
    get_test_db.commit()

    my_exercise = exercise_crud.get_many_for_owner(get_test_db, owner_id=u.id)
    assert len(my_exercise) == n_to_change and [
        isinstance(exercise, Exercise) and exercise.owner_id == u.id
        for exercise in my_exercise
    ]


def test_should_create_exercise(
    get_test_db, seed_exercise_types, seed_levels, seed_body_parts
):
    # given
    first_user = seed_superuser("test")
    level = level_crud.get_one(get_test_db, id=1)
    bodypart = bodypart_crud.get_one(get_test_db, id=1)
    exercise_type = exercise_type_crud.get_one(get_test_db, id=1)

    # when
    exercise_create = ExerciseCreate(
        name="Test Exercise",
        description="This is test exercise",
        level_id=level.id,
        target_body_part_id=bodypart.id,
        exercise_type_id=exercise_type.id,
    )

    exercise: Exercise = exercise_crud.create_with_owner(
        get_test_db, exercise_create, owner_id=first_user.id
    )

    # then
    fetched_exercise: Exercise = exercise_crud.get_one(
        get_test_db, Exercise.id == exercise.id
    )

    assert exercise is not None and isinstance(exercise, Exercise)
    assert fetched_exercise == exercise
    assert fetched_exercise.level == level
    assert fetched_exercise.target_body_part == bodypart
    assert fetched_exercise.exercise_type == exercise_type


def test_should_get_exercise_by_id_and_by_name(get_test_db, seed_test_database):
    ex = exercise_crud.get_one(get_test_db, id=1)
    name = ex.name
    assert ex is not None and isinstance(ex, Exercise)

    ex = exercise_crud.get_one(get_test_db, name=name)
    assert ex is not None and isinstance(ex, Exercise)


def test_should_update_exercise(get_test_db, seed_test_database):
    exercise = exercise_crud.get_one(get_test_db, id=1)
    assert exercise is not None and isinstance(exercise, Exercise)

    exercise_update = ExerciseUpdate(
        name="Updated Exercise",
        description="This is updated exercise",
        level_id=1,
        target_body_part_id=1,
        exercise_type_id=1,
    )

    exercise = exercise_crud.update(get_test_db, exercise, exercise_update)
    assert exercise is not None and isinstance(exercise, Exercise)
    assert exercise.name == exercise_update.name
    assert exercise.description == exercise_update.description
    assert exercise.level_id == exercise_update.level_id
    assert exercise.target_body_part_id == exercise_update.target_body_part_id
    assert exercise.exercise_type_id == exercise_update.exercise_type_id


def test_should_not_update_exercise_if_not_found(get_test_db):
    exercise_update = ExerciseUpdate(
        name="Updated Exercise",
        description="This is updated exercise",
        level_id=1,
        target_body_part_id=1,
        exercise_type_id=1,
    )
    with pytest.raises(Exception) as exc:
        exercise = exercise_crud.update(get_test_db, None, exercise_update)


def test_should_not_update_exercise_if_invalid_dependencies(
    get_test_db, seed_test_database
):
    exercise = exercise_crud.get_one(get_test_db, id=1)

    exercise_update = ExerciseUpdate(
        name="Updated Exercise",
        target_body_part_id=21321321,
    )
    with pytest.raises(IntegrityError) as exc:
        exercise = exercise_crud.update(get_test_db, exercise, exercise_update)
    assert "violates foreign key constraint" in str(exc.value)


def test_should_delete_exercise(get_test_db, seed_test_database):
    exercise = exercise_crud.get_one(get_test_db, id=1)
    exercise_crud.delete(get_test_db, exercise)
    exercise = exercise_crud.get_one(get_test_db, id=1)
    assert exercise is None
