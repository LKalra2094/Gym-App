# Deployment Guide - Supabase Setup

This guide will help you set up and deploy the Gym Progress Tracker application using Supabase as the database provider.

## 1. Supabase Setup

### Create a New Project
1. Go to [Supabase](https://supabase.com) and sign up/login
2. Click "New Project"
3. Fill in the project details:
   - Name: "Gym Progress Tracker"
   - Database Password: Create a strong password
   - Region: Choose the closest to your users
   - Pricing Plan: Free tier

### Get Database Connection Details
1. Go to Project Settings > Database
2. Find the connection string under "Connection string"
3. Copy the connection string and replace `[YOUR-PASSWORD]` with your database password

## 2. Environment Configuration

Create a `.env` file in your project root with the following variables:

```env
DATABASE_URL=your_supabase_connection_string
SECRET_KEY=generate_a_secure_random_key
RESEND_API_KEY=your_resend_api_key
RESEND_FROM_EMAIL=your_verified_email
```

To generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 3. Database Migration

1. Update `alembic.ini` with your Supabase connection string:
```ini
sqlalchemy.url = your_supabase_connection_string
```

2. Run the migrations:
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

## 4. Security Configuration

1. Go to Supabase Dashboard > Authentication > Policies
2. Copy and paste the contents of `supabase/security_policies.sql` into the SQL editor
3. Run the SQL to set up security policies

## 5. Email Configuration

1. Sign up for [Resend](https://resend.com)
2. Get your API key
3. Add your domain and verify it
4. Update the `.env` file with your Resend API key and verified email

## 6. Testing the Setup

1. Start the application:
```bash
uvicorn app.main:app --reload
```

2. Test the endpoints:
   - Register a new user
   - Create a workout
   - Add exercises
   - Log exercise progress

## 7. Monitoring and Maintenance

### Database Monitoring
1. Go to Supabase Dashboard > Database
2. Monitor:
   - Database size
   - Query performance
   - Connection count

### Backups
- Supabase automatically creates daily backups
- Backups are retained for 7 days on the free tier
- Consider upgrading for longer retention

### Scaling
Monitor these metrics to know when to upgrade:
- Database size approaching 500MB
- Bandwidth approaching 2GB
- Active users approaching 50,000

## 8. Troubleshooting

### Common Issues

1. **Connection Issues**
   - Verify DATABASE_URL is correct
   - Check if IP is allowed in Supabase
   - Ensure database is active

2. **Migration Issues**
   ```bash
   # If migrations fail
   alembic downgrade -1
   alembic upgrade head
   ```

3. **Email Issues**
   - Verify Resend API key
   - Check email domain verification
   - Test email sending

4. **Performance Issues**
   - Check query performance in Supabase dashboard
   - Verify indexes are created
   - Monitor connection pool

## 9. Security Best Practices

1. **Regular Updates**
   - Keep dependencies updated
   - Monitor security advisories
   - Update Supabase client

2. **Access Control**
   - Review RLS policies regularly
   - Monitor failed authentication attempts
   - Keep user roles minimal

3. **Data Protection**
   - Regular backup verification
   - Monitor for suspicious activity
   - Implement rate limiting

## 10. Support and Resources

- [Supabase Documentation](https://supabase.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Alembic Documentation](https://alembic.sqlalchemy.org) 