-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE workouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercises ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercise_logs ENABLE ROW LEVEL SECURITY;

-- Users table policies
CREATE POLICY "Users can view their own data"
ON users
FOR SELECT
USING (auth.uid()::uuid = id);

CREATE POLICY "Users can update their own data"
ON users
FOR UPDATE
USING (auth.uid()::uuid = id);

-- Workouts table policies
CREATE POLICY "Users can view their own workouts"
ON workouts
FOR SELECT
USING (auth.uid()::uuid = user_id);

CREATE POLICY "Users can create their own workouts"
ON workouts
FOR INSERT
WITH CHECK (auth.uid()::uuid = user_id);

CREATE POLICY "Users can update their own workouts"
ON workouts
FOR UPDATE
USING (auth.uid()::uuid = user_id);

CREATE POLICY "Users can delete their own workouts"
ON workouts
FOR DELETE
USING (auth.uid()::uuid = user_id);

-- Exercises table policies
CREATE POLICY "Users can view exercises in their workouts"
ON exercises
FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM workouts
        WHERE workouts.id = exercises.workout_id
        AND workouts.user_id = auth.uid()::uuid
    )
);

CREATE POLICY "Users can create exercises in their workouts"
ON exercises
FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM workouts
        WHERE workouts.id = exercises.workout_id
        AND workouts.user_id = auth.uid()::uuid
    )
);

CREATE POLICY "Users can update exercises in their workouts"
ON exercises
FOR UPDATE
USING (
    EXISTS (
        SELECT 1 FROM workouts
        WHERE workouts.id = exercises.workout_id
        AND workouts.user_id = auth.uid()::uuid
    )
);

CREATE POLICY "Users can delete exercises in their workouts"
ON exercises
FOR DELETE
USING (
    EXISTS (
        SELECT 1 FROM workouts
        WHERE workouts.id = exercises.workout_id
        AND workouts.user_id = auth.uid()::uuid
    )
);

-- Exercise logs table policies
CREATE POLICY "Users can view their own exercise logs"
ON exercise_logs
FOR SELECT
USING (auth.uid()::uuid = user_id);

CREATE POLICY "Users can create their own exercise logs"
ON exercise_logs
FOR INSERT
WITH CHECK (auth.uid()::uuid = user_id);

CREATE POLICY "Users can update their own exercise logs"
ON exercise_logs
FOR UPDATE
USING (auth.uid()::uuid = user_id);

CREATE POLICY "Users can delete their own exercise logs"
ON exercise_logs
FOR DELETE
USING (auth.uid()::uuid = user_id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_workouts_user_id ON workouts(user_id);
CREATE INDEX IF NOT EXISTS idx_exercises_workout_id ON exercises(workout_id);
CREATE INDEX IF NOT EXISTS idx_exercise_logs_user_id ON exercise_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_exercise_logs_exercise_id ON exercise_logs(exercise_id);
CREATE INDEX idx_exercise_logs_date ON exercise_logs(date); 