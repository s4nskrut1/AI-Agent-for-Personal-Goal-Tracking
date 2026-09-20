"""
GoalMate — Automatic Database Seeding for Default Account & Sanskriti's Goals.
Ensures that whenever GoalMate is deployed to a new environment (like Render cloud),
the default Sanskriti account and her 3 goals are immediately ready.
"""
from datetime import date, datetime, timedelta
from backend.models import User, Goal, Milestone, Task, ActivityLog, SessionLocal
from backend.auth import hash_password


def seed_default_user_and_goals():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "sanskriti@example.com").first()
        if not user:
            user = User(
                name="Sanskriti",
                email="sanskriti@example.com",
                password_hash=hash_password("password123")
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print("[SEED] Default user Sanskriti created.")
        else:
            # Update password hash in case it was a mock hash
            user.password_hash = hash_password("password123")
            db.commit()

        # Check if goals exist for this user
        existing_goals = db.query(Goal).filter(Goal.user_id == user.id).count()
        if existing_goals == 0:
            today = date(2026, 9, 20)

            # 1. Learn DSA
            g1_start = date(2026, 9, 17)
            g1_duration = 45
            g1 = Goal(
                user_id=user.id,
                title="Learn DSA",
                description="Master Data Structures and Algorithms with daily practice problems.",
                category="Computer Science",
                duration_days=g1_duration,
                start_date=g1_start,
                deadline=g1_start + timedelta(days=g1_duration),
                status="active"
            )
            db.add(g1)
            db.commit()
            db.refresh(g1)

            g1_ms_data = [
                ("Arrays, Strings & Two Pointers", [
                    ("Array basics & Two Sum problem", 0, True),
                    ("Best Time to Buy and Sell Stock", 1, True),
                    ("Contains Duplicate & Valid Anagram", 2, True),
                    ("Sliding Window Maximum & Longest Substring", 3, False),
                    ("3Sum and Container With Most Water", 4, False),
                    ("Valid Palindrome & Product of Array Except Self", 5, False),
                    ("Longest Repeating Character Replacement", 6, False),
                    ("Minimum Window Substring practice", 7, False),
                ]),
                ("Linked Lists & Fast-Slow Pointers", [
                    ("Reverse a Linked List & Merge Two Sorted Lists", 8, False),
                    ("Linked List Cycle & Reorder List", 9, False),
                    ("Remove Nth Node from End of List", 10, False),
                    ("Copy List with Random Pointer", 11, False),
                    ("Merge K Sorted Lists", 12, False),
                    ("LRU Cache Design", 13, False),
                    ("Reverse Nodes in k-Group", 14, False),
                ]),
                ("Stacks, Queues & Binary Search", [
                    ("Valid Parentheses & Min Stack", 15, False),
                    ("Evaluate Reverse Polish Notation", 16, False),
                    ("Daily Temperatures & Monotonic Stack", 17, False),
                    ("Binary Search & Search in Rotated Sorted Array", 18, False),
                    ("Find Minimum in Rotated Sorted Array", 19, False),
                    ("Time Based Key-Value Store", 20, False),
                    ("Median of Two Sorted Arrays", 21, False),
                ]),
                ("Trees, BST & Tree Traversals", [
                    ("Invert Binary Tree & Max Depth of Binary Tree", 22, False),
                    ("Diameter of Binary Tree & Balanced Tree", 23, False),
                    ("Same Tree & Subtree of Another Tree", 24, False),
                    ("Lowest Common Ancestor of a BST", 25, False),
                    ("Binary Tree Level Order Traversal", 26, False),
                    ("Validate Binary Search Tree", 27, False),
                    ("Kth Smallest Element in a BST", 28, False),
                ]),
                ("Graphs, BFS/DFS & Shortest Path", [
                    ("Number of Islands & Max Area of Island", 29, False),
                    ("Clone Graph & Pacific Atlantic Water Flow", 30, False),
                    ("Surrounded Regions & Rotting Oranges", 31, False),
                    ("Course Schedule I & II (Topological Sort)", 32, False),
                    ("Redundant Connection & Graph Valid Tree", 33, False),
                    ("Word Ladder & Dijkstra Shortest Path", 34, False),
                    ("Network Delay Time", 35, False),
                ]),
                ("Dynamic Programming & System Design Basics", [
                    ("Climbing Stairs & Min Cost Climbing Stairs", 36, False),
                    ("House Robber I & II", 37, False),
                    ("Longest Palindromic Substring", 38, False),
                    ("Coin Change & Partition Equal Subset Sum", 39, False),
                    ("Longest Increasing Subsequence", 40, False),
                    ("Edit Distance & Unique Paths", 41, False),
                    ("Target Sum & Maximum Subarray", 42, False),
                    ("System Design: Rate Limiter & URL Shortener", 43, False),
                    ("Final Review: Comprehensive LeetCode Mock Interview", 44, False),
                ]),
            ]

            for order_idx, (ms_title, tasks_list) in enumerate(g1_ms_data):
                ms = Milestone(goal_id=g1.id, title=ms_title, order_index=order_idx)
                db.add(ms)
                db.commit()
                db.refresh(ms)
                for t_title, day_offset, is_done in tasks_list:
                    t_date = g1_start + timedelta(days=day_offset)
                    t = Task(
                        goal_id=g1.id,
                        milestone_id=ms.id,
                        title=t_title,
                        scheduled_date=t_date,
                        estimated_duration="45 min",
                        status="completed" if is_done else "pending",
                        completed_at=datetime(2026, 9, 17 + day_offset, 18, 30) if is_done else None
                    )
                    db.add(t)
            db.commit()

            # 2. Build an App
            g2_start = date(2026, 9, 10)
            g2_duration = 60
            g2 = Goal(
                user_id=user.id,
                title="Build an App",
                description="Develop and ship a full-stack goal tracking application with agentic AI.",
                category="Development",
                duration_days=g2_duration,
                start_date=g2_start,
                deadline=g2_start + timedelta(days=g2_duration),
                status="active"
            )
            db.add(g2)
            db.commit()
            db.refresh(g2)

            g2_ms_data = [
                ("Planning & Architecture", [
                    ("Define app idea and core features", date(2026, 9, 10), True),
                    ("Design system architecture and state flow", date(2026, 9, 12), False),
                    ("Set up project repository and environment", date(2026, 9, 16), True),
                ]),
                ("Database Design & Wireframes", [
                    ("Design database schema and wireframes", date(2026, 9, 13), True),
                    ("Configure SQLAlchemy ORM models and migrations", date(2026, 9, 18), False),
                    ("Seed initial baseline verification datasets", date(2026, 9, 19), False),
                ]),
                ("Core Backend Services", [
                    ("Implement REST endpoints for task toggles", today, False),
                    ("Implement rescheduling and streak calculation logic", date(2026, 9, 22), False),
                    ("Add robust error handling and logging services", date(2026, 9, 25), False),
                ]),
                ("Frontend Interface & Reactive State", [
                    ("Build responsive 3-column dashboard shell", date(2026, 9, 28), False),
                    ("Develop interactive SVG progress curves and charts", date(2026, 10, 2), False),
                    ("Implement anime theme aesthetics and glassmorphism cards", date(2026, 10, 6), False),
                ]),
                ("AI Agent Tool Calling Integration", [
                    ("Connect Google Gemini API with function calling", date(2026, 10, 12), False),
                    ("Integrate Tavily web search for learning resources", date(2026, 10, 18), False),
                    ("Test conversational goal breakdown workflows", date(2026, 10, 24), False),
                ]),
                ("Production Hardening & Deployment", [
                    ("Configure Docker and dynamic cloud PORT binding", date(2026, 10, 30), False),
                    ("Set up production environment variables and auth keys", date(2026, 11, 4), False),
                    ("Deploy live instance to Render and verify uptime", date(2026, 11, 8), False),
                ]),
            ]

            for order_idx, (ms_title, tasks_list) in enumerate(g2_ms_data):
                ms = Milestone(goal_id=g2.id, title=ms_title, order_index=order_idx)
                db.add(ms)
                db.commit()
                db.refresh(ms)
                for t_title, t_date, is_done in tasks_list:
                    t = Task(
                        goal_id=g2.id,
                        milestone_id=ms.id,
                        title=t_title,
                        scheduled_date=t_date,
                        estimated_duration="45 min",
                        status="completed" if is_done else "pending",
                        completed_at=datetime.combine(t_date, datetime.min.time()) if is_done else None
                    )
                    db.add(t)
            db.commit()

            # 3. Sports Daily Routine for Volleyball
            g3_start = date(2026, 9, 18)
            g3_duration = 30
            g3 = Goal(
                user_id=user.id,
                title="Sports Daily Routine for Volleyball",
                description="Dedicated daily conditioning, agility, and volleyball technique routine.",
                category="Sports / Fitness",
                duration_days=g3_duration,
                start_date=g3_start,
                deadline=g3_start + timedelta(days=g3_duration),
                status="active"
            )
            db.add(g3)
            db.commit()
            db.refresh(g3)

            g3_ms_data = [
                ("Warmup & Agility Conditioning", [
                    ("Dynamic Warmup & 3x10 Agility Ladder drills", date(2026, 9, 18), True),
                    ("Footwork drills & approach jump practice", date(2026, 9, 19), True),
                    ("Forearm passing accuracy against target wall (40 reps)", today, False),
                    ("Shuttle sprints & quick court directional changes", date(2026, 9, 21), False),
                    ("Core stability workout: Planks and Russian twists", date(2026, 9, 22), False),
                    ("Recovery jog & full-body static stretching", date(2026, 9, 23), False),
                ]),
                ("Serve & Receive Technique", [
                    ("Standing float serve practice (30 repetitions)", date(2026, 9, 24), False),
                    ("Jump float serve footwork & ball toss timing", date(2026, 9, 25), False),
                    ("Low-platform serve receive reaction drills", date(2026, 9, 26), False),
                    ("Target serve drill: Corner zones precision", date(2026, 9, 27), False),
                    ("High-velocity serve reception positioning", date(2026, 9, 28), False),
                    ("Video technique review & serve consistency log", date(2026, 9, 29), False),
                ]),
                ("Spike & Block Footwork Drills", [
                    ("3-step approach footwork & arm swing repetition", date(2026, 9, 30), False),
                    ("Lateral blocking shuffle & hand penetration at net", date(2026, 10, 1), False),
                    ("Tip & roll shot placement around block", date(2026, 10, 2), False),
                    ("Transition from defense to quick attacking run", date(2026, 10, 3), False),
                    ("Middle blocker read-and-react footwork", date(2026, 10, 4), False),
                    ("Power hitting drills off high sets", date(2026, 10, 5), False),
                ]),
                ("Team Rotations & Defensive Coverage", [
                    ("Rotation 1 through 6 positioning walk-through", date(2026, 10, 6), False),
                    ("Perimeter defense & tip coverage responsibilities", date(2026, 10, 7), False),
                    ("Free ball transition & setter release practice", date(2026, 10, 8), False),
                    ("Pancake and dive recovery technique drills", date(2026, 10, 9), False),
                    ("Covering hitter off block rebound drills", date(2026, 10, 10), False),
                    ("Simulated rally play & defensive communication", date(2026, 10, 11), False),
                ]),
                ("Match Conditioning & Vertical Jump Training", [
                    ("Plyometrics: Box jumps & depth jumps 4x8", date(2026, 10, 12), False),
                    ("Full-court scrimmage simulation (5 sets)", date(2026, 10, 13), False),
                    ("Weighted squat jumps & hamstring curls", date(2026, 10, 14), False),
                    ("Endurance shuttle runs: 10 sets of baseline to net", date(2026, 10, 15), False),
                    ("Cool-down yoga and mobility routine for shoulders", date(2026, 10, 16), False),
                    ("Final fitness evaluation & vertical leap test", date(2026, 10, 17), False),
                ]),
            ]

            for order_idx, (ms_title, tasks_list) in enumerate(g3_ms_data):
                ms = Milestone(goal_id=g3.id, title=ms_title, order_index=order_idx)
                db.add(ms)
                db.commit()
                db.refresh(ms)
                for t_title, t_date, is_done in tasks_list:
                    t = Task(
                        goal_id=g3.id,
                        milestone_id=ms.id,
                        title=t_title,
                        scheduled_date=t_date,
                        estimated_duration="30 min",
                        status="completed" if is_done else "pending",
                        completed_at=datetime.combine(t_date, datetime.min.time()) if is_done else None
                    )
                    db.add(t)
            db.commit()

            print("[SEED] Sanskriti's 3 goals automatically seeded.")
    except Exception as e:
        print(f"[SEED ERROR] {e}")
    finally:
        db.close()
