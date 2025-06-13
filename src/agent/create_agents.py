import sqlite3
import json
import random


def main():
    conn = sqlite3.connect("agents.db")
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS agents (
        agent_id TEXT PRIMARY KEY,
        name TEXT,
        gender TEXT,
        languages TEXT,   
        skills TEXT,      
        is_available INTEGER,
        current_load INTEGER,
        experience INTEGER
    );
    """
    )

    male_first_names = [
        "Youssef",
        "Rachid",
        "Mohamed",
        "Amine",
        "Adil",
        "Zakaria",
        "Hicham",
        "Nabil",
        "Soufiane",
        "Omar",
    ]

    female_first_names = [
        "Kenza",
        "Sara",
        "Imane",
        "Salma",
        "Aya",
        "Zineb",
        "Nour",
        "Samira",
        "Asma",
        "Latifa",
    ]

    last_names = [
        "El Fassi",
        "El Idrissi",
        "Bouazizi",
        "Zouaoui",
        "Bennani",
        "Cherkaoui",
        "El Amrani",
        "Ouarzazi",
        "El Mansouri",
        "Bakkali",
    ]

    genders = ["Male", "Female"]
    language_options = ["en", "es", "fr", "de", "it", "pt"]
    skill_options = [
        "product inquiry",
        "technical support",
        "billing issue",
        "complaint",
        "feedback",
        "account cancellation",
        "order status",
        "refund request",
        "appointment scheduling",
        "service activation",
        "farewell",
    ]

    def random_agent(i):
        agent_id = f"A{i:03d}"
        gender = random.choice(genders)
        if gender == "Male":
            first_name = random.choice(male_first_names)
        else:
            first_name = random.choice(female_first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"

        languages = random.sample(language_options, k=random.randint(1, 3))
        skills = random.sample(skill_options, k=random.randint(1, 3))
        is_available = random.choice([0, 1])
        current_load = random.randint(0, 5)
        experience = random.randint(1, 10)

        return (
            agent_id,
            name,
            gender,
            json.dumps(languages),
            json.dumps(skills),
            is_available,
            current_load,
            experience,
        )

    agents_data = [random_agent(i) for i in range(1, 101)]

    cursor.executemany(
        """
    INSERT INTO agents (agent_id, name, gender, languages, skills, is_available, current_load, experience)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        agents_data,
    )

    conn.commit()

    print("inserted 100 random agents into 'agents' table")

    cursor.execute("SELECT * FROM agents LIMIT 3")
    for row in cursor.fetchall():
        print(row)

    conn.close()


if __name__ == "__main__":
    main()
