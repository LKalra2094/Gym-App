# Gym Progress Tracker

A web application for tracking workout progress, exercises, and weight progression over time.

## Features

- Custom workout creation and management
- Exercise tracking with sets and reps
- Weight progression tracking
- Data visualization with customizable time periods
- Support for both kg and lbs weight units

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Supabase Database:
   - Go to [Supabase](https://supabase.com) and create a free account
   - Create a new project
   - Once created, go to Project Settings > Database
   - Copy the connection string (it looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres`)

4. Create a `.env` file with the following variables:
```
DATABASE_URL=your_supabase_connection_string
SECRET_KEY=your-secret-key-here
RESEND_API_KEY=your-resend-api-key
RESEND_FROM_EMAIL=your-verified-email@domain.com
```

5. Initialize the database:
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

6. Run the application:
```bash
uvicorn app.main:app --reload
```

## Database Schema

The application uses the following main tables:

1. **users**
   - id (Primary Key)
   - email
   - password (hashed)
   - role
   - is_verified
   - verification_token
   - reset_token
   - reset_token_expires
   - preferred_weight_unit
   - created_at
   - updated_at

2. **workouts**
   - id (Primary Key)
   - name
   - user_id (Foreign Key)
   - created_at
   - updated_at

3. **exercises**
   - id (Primary Key)
   - name
   - workout_id (Foreign Key)
   - created_at
   - updated_at

4. **exercise_logs**
   - id (Primary Key)
   - exercise_id (Foreign Key)
   - user_id (Foreign Key)
   - weight
   - weight_unit
   - reps
   - sets
   - date
   - created_at

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Database Migrations

To create a new migration after model changes:
```bash
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Testing

Run tests with:
```bash
pytest
```

## Testing Structure

All unit tests are located in `tests/unit/` for clear separation from integration or end-to-end tests. Each utility module and core function has a corresponding test file with comprehensive coverage and clear docstrings. 

- To run all unit tests:
  ```bash
  python -m pytest tests/unit/ -v
  ```

- All test files and functions are documented for clarity and maintainability.

## Integration Tests

Integration tests are located in `tests/integration/`. These tests verify that your application works correctly with external services (e.g., email sending via resend).

- To run all integration tests:
  ```bash
  python -m pytest tests/integration/ -v
  ```

- All integration test files and functions are documented for clarity and maintainability.

## Deployment

### Supabase Configuration

1. **Security Rules**:
   - Enable Row Level Security (RLS)
   - Create policies for each table:
     ```sql
     -- Example policy for exercise_logs
     CREATE POLICY "Users can only access their own exercise logs"
     ON exercise_logs
     FOR ALL
     USING (auth.uid() = user_id);
     ```

2. **Database Backups**:
   - Supabase automatically creates daily backups
   - Backups are retained for 7 days on the free tier

3. **Scaling**:
   - Free tier includes:
     - 500MB database
     - 2GB bandwidth
     - 50,000 monthly active users
   - Upgrade when needed for:
     - More storage
     - Higher bandwidth
     - Additional features

## Troubleshooting

### Common Issues

1. **Database Connection**:
   - Verify DATABASE_URL in .env
   - Check if Supabase project is active
   - Ensure IP is allowed in Supabase dashboard

2. **Migrations**:
   - If migrations fail, try:
     ```bash
     alembic downgrade -1
     alembic upgrade head
     ```

3. **Authentication**:
   - Verify SECRET_KEY in .env
   - Check email configuration
   - Ensure RESEND_API_KEY is valid

## New Data Model Description

- **Workouts**: Users can create, view, update, and delete workouts. Each workout has a name.
- **Exercises**: Within each workout, users can add exercises. Each exercise has a name.
- **Logging**: Users can log their performance for each exercise, recording metrics like weight, reps, sets, and duration.
- **Progress Tracking**: The app provides visualizations to track progress over time for specific exercises.
- **User Authentication**: Secure user registration and login using JWT.
- **Weight Unit Preference**: Users can set their preferred weight unit (kg or lbs).

### Tech Stack

- **Backend**: FastAPI, Python 3.11, PostgreSQL
- **ORM**: SQLAlchemy with `asyncio` support

## New Tables Description

1. **users**
   - id (Primary Key)
   - email
   - password (hashed)
   - role
   - is_verified
   - verification_token
   - reset_token
   - reset_token_expires
   - preferred_weight_unit
   - created_at
   - updated_at

2. **workouts**
   - id (Primary Key)
   - name
   - user_id (Foreign Key)
   - created_at
   - updated_at

3. **exercises**
   - id (Primary Key)
   - name
   - workout_id (Foreign Key)
   - created_at
   - updated_at

4. **exercise_logs**
   - id (Primary Key)
   - exercise_id (Foreign Key)
   - user_id (Foreign Key)
   - weight
   - weight_unit
   - reps
   - sets
   - date
   - created_at

## New Columns Description

1. **users**
   - id
   - name
   - slug
   - user_id
   - created_at
   - updated_at

2. **exercises**
   - id
   - name
   - slug
   - category
   - workout_id
   - user_id
   - created_at
   - updated_at

3. **exercise_logs**
   - id
   - exercise_id
   - user_id
   - weight
   - weight_unit
   - reps
   - sets
   - date
   - created_at 