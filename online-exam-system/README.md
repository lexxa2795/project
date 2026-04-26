# Online Examination System 📝

A complete web-based examination system with separate interfaces for admins and students. Built with Flask and SQLite.

## Features ✨

### Admin Features
- ✅ Create and manage exams
- ✅ Add questions with multiple choice options
- ✅ Set correct answers and marks per question
- ✅ View all created exams
- ✅ Manage exam status

### Student Features
- ✅ View available exams
- ✅ Take exams with timer
- ✅ Answer multiple choice questions
- ✅ Submit exams automatically when time runs out
- ✅ View results with marks breakdown
- ✅ See answer details (correct vs attempted)

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **No External Dependencies:** Pure CSS styling, no Bootstrap or frameworks

## Installation & Setup

### Prerequisites
- Python 3.7+
- pip

### Steps

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd online-exam-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open in browser**
   ```
   http://localhost:5000
   ```

## Demo Credentials

### Admin Login
- **Username:** admin
- **Password:** password
- **Role:** Admin (can create exams and add questions)

### Student Login
- **Username:** student1
- **Password:** password
- **Role:** Student (can take exams)

## Usage Guide

### For Admins

1. **Login** with admin credentials
2. **Create Exam**
   - Fill in exam title, description, duration, and total marks
   - Click "Create Exam"
3. **Manage Questions**
   - Click "Manage Questions" on an exam
   - Switch to "Add Question" tab
   - Enter question text, all 4 options, select correct answer, and marks
   - Click "Add Question"
4. **View Questions**
   - Questions tab shows all added questions with correct answers

### For Students

1. **Login** with student credentials
2. **View Available Exams**
   - See all exams created by admins
   - View duration and total marks
3. **Take Exam**
   - Click "Start Exam"
   - Answer questions before time runs out
   - Timer shows remaining time
   - Answers are automatically saved
4. **Submit Exam**
   - Click "Submit Exam" or wait for timer to expire
   - System automatically submits when time is up
5. **View Results**
   - See marks obtained and percentage
   - Check if you passed or failed (40% is passing)
   - View detailed answer breakdown

## Database Schema

### Tables

- **users**: Stores user information (username, email, password, role)
- **exams**: Stores exam details (title, duration, marks, created_by)
- **questions**: Stores questions and options (exam_id, question_text, options, correct_answer, marks)
- **student_answers**: Stores student responses (exam_id, student_id, question_id, answer, is_correct)
- **exam_results**: Stores exam results (exam_id, student_id, total_marks, obtained_marks, percentage, status)

## Features in Detail

### Timer Functionality
- Real-time countdown timer
- Automatic submission when time expires
- Prevents submission after time is up

### Marking System
- Each question has individual marks
- Correct answers award full marks
- Wrong/unanswered questions get 0 marks
- Total marks and percentage calculated automatically
- Pass/Fail status based on 40% threshold

### Security Features
- Session-based authentication
- Admin-only operations protected
- Student can only view their own results
- Questions visible only during exam time

## File Structure

```
online-exam-system/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── exam_system.db                  # SQLite database (auto-created)
└── templates/
    ├── login.html                  # Login & Registration page
    ├── admin_dashboard.html        # Admin interface
    └── student_dashboard.html      # Student interface
```

## Future Enhancements

- [ ] Password hashing (use werkzeug.security)
- [ ] Email verification
- [ ] Forgot password functionality
- [ ] Question bank/categories
- [ ] Different exam types (essay, matching, etc.)
- [ ] Leaderboard/Rankings
- [ ] Exam analytics for admins
- [ ] Question import/export (CSV, JSON)
- [ ] Negative marking
- [ ] Image support in questions

## Troubleshooting

**Can't login:**
- Check if database is created (exam_system.db should exist)
- Restart the Flask app
- Clear browser cookies and try again

**Timer not working:**
- Check browser console for JavaScript errors
- Ensure JavaScript is enabled
- Try a different browser

**Questions not saving:**
- Ensure all fields are filled
- Check network connectivity
- Verify SQLite permissions

## License

MIT License - Feel free to use this project for learning and educational purposes.

## Support

For issues or questions, please create an issue in the repository.

---

**Happy Exams! 📚**
