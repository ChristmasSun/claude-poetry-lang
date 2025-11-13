# Lament Empathy System - Quick Start Guide

## 🚀 Get Started in 2 Minutes

### Installation
The empathy system is built-in! No additional setup required.

### Basic Usage

#### 1. Run Code with Empathetic Errors
```bash
python3 lament/cli.py run your_file.lament
```

Errors will automatically include:
- Compassionate explanations
- Auto-suggested fixes
- Fatigue detection
- Pattern recognition
- Concept explanations

#### 2. Conduct Code Therapy
```bash
python3 lament/cli.py therapy your_file.lament
```

Get a conversation-style analysis of your codebase's emotional health.

### Try the Demo

Run the comprehensive showcase:
```bash
cd /home/user/claude-poetry-lang
python3 demo_empathy_showcase.py
```

Or test therapy directly:
```bash
python3 lament/cli.py therapy demo_therapy_clean.lament
```

---

## 💡 What Makes This Special?

### Empathetic Errors Example

**Before (Traditional):**
```
Error: undefined variable 'usrname'
  at line 5
```

**After (Lament):**
```
💔 LAMENT ERROR 💔

I sense your frustration...

I searched for 'usrname' in all the timelines,
but it was never remembered.

💡 Understanding the issue:
  In Lament, variables must be 'remembered' before use.

✨ Suggested fixes:
  1. Did you mean 'user_name'? (Check spelling)
  2. Add: remember usrname = <value>

Need more help? I'm here for you.

Session: 7a3f9b2e | Time coding: 12.5 min | Errors: 2
```

### Code Therapy Example

```bash
$ python3 lament/cli.py therapy mycode.lament

🛋️  CODE THERAPY SESSION 🛋️

Welcome. I'm here to listen.
Let's talk about how your code is feeling...

What's troubling you?
  💔 Function 'calculate_tax' is never called - feeling abandoned
  😰 Function 'validate' has excessive branching
  🕳️  Your code goes deep (6 levels)

Let's work through this together...

1. 🗣️  'calculate_tax' needs a purpose or it's time to let it go
2. 🧘 'validate' is anxious. Why so many guards?
3. 🕳️  Come back to the surface. Flatten it.

We've had 3 sessions together.
Your codebase is healing! Health improved by 15.2 points.
```

---

## 🎯 Key Features

### Session Tracking
- Monitors coding time
- Detects error patterns
- Identifies repeated mistakes
- Stored in `~/.lament/session.json`

### Fatigue Detection
After 4+ hours of coding:
```
⚠ FATIGUE DETECTED: HIGH ⚠
Consider taking a break. Fresh eyes see solutions faster.
```

### Auto-Suggestions
- Typo detection for variable names
- Context-aware fix recommendations
- Specific templates per error type

### Concept Explanations
Every error includes:
- What the concept means
- Why this error happens
- How to fix it

### Code Therapy
Identifies:
- Lonely functions (never called)
- Anxious code (excessive guards)
- Complex functions (doing too much)
- Deep nesting (lost in layers)

Provides:
- Conversation-style recommendations
- Long-term health tracking
- Personalized refactoring suggestions

---

## 📖 File Examples

### Example 1: Demo with Errors
Create `test_empathy.lament`:
```lament
remember user_name = "Alice"
confess usrname
```

Run it:
```bash
python3 lament/cli.py run test_empathy.lament
```

You'll get an empathetic error with typo detection!

### Example 2: Demo for Therapy
Create `test_therapy.lament`:
```lament
sigh unused_function() {
    remember x = 10
    exhale x
}

sigh overly_defensive(val) {
    if val != void {
        if is_numb(val) {
            if val > 0 {
                if val < 100 {
                    confess "valid"
                }
            }
        }
    }
}

overly_defensive(42)
```

Run therapy:
```bash
python3 lament/cli.py therapy test_therapy.lament
```

The therapist will identify:
- Lonely function `unused_function`
- Anxious function `overly_defensive`

---

## 🔧 Architecture

### Core Components

```
lament/empathy.py
├── SessionManager          # Tracks developer sessions
├── EmpathyEngine          # Creates empathetic errors
├── CodeTherapist          # Conducts therapy sessions
└── Integration hooks      # Connects to interpreter
```

### Data Storage

```
~/.lament/
├── session.json          # Current coding session
└── therapy_history.json  # Long-term therapy records
```

---

## 🎨 Customization

### Add New Error Types

Edit `lament/empathy.py`:

```python
ERROR_EXPLANATIONS = {
    'YOUR_ERROR': {
        'concept': "What it means",
        'common_cause': "Why it happens",
        'fix_template': "How to fix"
    }
}
```

### Custom Therapy Recommendations

Modify `CodeTherapist._generate_therapy_recommendations()`:

```python
if your_condition:
    recommendations.append(
        f"🎯 Your custom advice here"
    )
```

---

## 🌟 Philosophy

### Core Principles

1. **Errors should help, not blame**
   - Every error is a teaching moment
   - Suggestions are specific and actionable
   - Tone is compassionate and supportive

2. **Developer wellbeing matters**
   - Fatigue detection prevents burnout
   - Pattern recognition helps learning
   - Break reminders promote health

3. **Code has feelings**
   - Lonely functions need purpose
   - Anxious code needs trust
   - Complex functions need simplification
   - Chaotic code needs structure

4. **Long-term relationships**
   - Therapy tracks progress over time
   - Improvements are celebrated
   - Setbacks are supported
   - Growth is encouraged

---

## 📚 Learn More

- **Full Documentation**: `EMPATHY_README.md`
- **Interactive Demo**: `python3 demo_empathy_showcase.py`
- **API Reference**: Inline docs in `lament/empathy.py`
- **Examples**: `demo_therapy_clean.lament`

---

## 🤝 Contributing

Want to make Lament more empathetic?

1. Add error type explanations
2. Improve typo detection
3. Create therapy recommendations
4. Write tests
5. Translate messages

---

## 💜 Support

Having trouble? The empathy system is here to help!

- Check error messages for suggestions
- Run therapy to understand code health
- Review `EMPATHY_README.md` for details
- Look at demo files for examples

---

## 🎭 Credits

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)

*"I sense your frustration. Let me help you through this."*

---

**Remember**: Code has feelings. Developers deserve compassion. Errors should help.

Welcome to Lament. The language that cares. 💜
