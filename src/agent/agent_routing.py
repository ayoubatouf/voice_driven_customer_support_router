from sqlalchemy import text


def find_agent(language, intent, gender, db_conn):
    queries = [
        # language + intent + gender
        (
            text(
                """
            SELECT agent_id FROM agents
            WHERE is_available = 1
            AND EXISTS (SELECT 1 FROM json_each(languages) WHERE value = :language)
            AND EXISTS (SELECT 1 FROM json_each(skills) WHERE value = :intent)
            AND gender = :gender
            ORDER BY experience DESC, current_load ASC
            LIMIT 1;
            """
            ),
            {"language": language, "intent": intent, "gender": gender},
        ),
        # language + gender
        (
            text(
                """
            SELECT agent_id FROM agents
            WHERE is_available = 1
            AND EXISTS (SELECT 1 FROM json_each(languages) WHERE value = :language)
            AND gender = :gender
            ORDER BY experience DESC, current_load ASC
            LIMIT 1;
            """
            ),
            {"language": language, "gender": gender},
        ),
        # english + intent + gender
        (
            text(
                """
            SELECT agent_id FROM agents
            WHERE is_available = 1
            AND EXISTS (SELECT 1 FROM json_each(languages) WHERE value = 'en')
            AND EXISTS (SELECT 1 FROM json_each(skills) WHERE value = :intent)
            AND gender = :gender
            ORDER BY experience DESC, current_load ASC
            LIMIT 1;
            """
            ),
            {"intent": intent, "gender": gender},
        ),
        # language only
        (
            text(
                """
            SELECT agent_id FROM agents
            WHERE is_available = 1
            AND EXISTS (SELECT 1 FROM json_each(languages) WHERE value = :language)
            ORDER BY experience DESC, current_load ASC
            LIMIT 1;
            """
            ),
            {"language": language},
        ),
        # english + intent only
        (
            text(
                """
            SELECT agent_id FROM agents
            WHERE is_available = 1
            AND EXISTS (SELECT 1 FROM json_each(languages) WHERE value = 'en')
            AND EXISTS (SELECT 1 FROM json_each(skills) WHERE value = :intent)
            ORDER BY experience DESC, current_load ASC
            LIMIT 1;
            """
            ),
            {"intent": intent},
        ),
        # final fallback
        (
            text(
                """
            SELECT agent_id FROM agents
            WHERE is_available = 1
            ORDER BY experience DESC, current_load ASC
            LIMIT 1;
            """
            ),
            {},
        ),
    ]

    for query, params in queries:
        result = db_conn.execute(query, params)
        row = result.first()
        if row:
            return row.agent_id
    return None


def get_agent_info(agent_id, db_conn):
    query = text(
        """
        SELECT agent_id, name, gender, languages, skills, experience, current_load, is_available
        FROM agents
        WHERE agent_id = :agent_id;
    """
    )
    result = db_conn.execute(query, {"agent_id": agent_id})
    row = result.first()
    if row:
        return dict(row._mapping)
    return None
