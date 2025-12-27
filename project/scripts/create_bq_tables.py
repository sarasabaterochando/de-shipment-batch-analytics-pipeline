import subprocess
from string import Template


CONFIG_PATH = "airflow/config/config.env"
SQL_TEMPLATE_DIM = "sql/dim_batch_shipment.sql"
SQL_TEMPLATE_FACT = "sql/fact_batch_shipment.sql"
OUTPUT_SQL = "/tmp/create_tables_rendered.sql"



def load_env(path):
    """
    Load the path with the predefined variables
    
    :param path: string with the path
    :return dict with the variables
    """
    env_vars = {}
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env_vars[key] = value
    return env_vars


def create_bigquery_table(sql_statement):
    """
    Creates the bigquery tables from a template previously created
    
    :param sql_statement: string with path to .sql file
    """
    try:
        env = load_env(CONFIG_PATH)

        # Read sql templates
        with open(sql_statement, "r") as f:
            template = Template(f.read())

        # Sustituir las variables
        rendered_sql = template.safe_substitute(env)

        # Save final SQL 
        with open(OUTPUT_SQL, "w") as f:
            f.write(rendered_sql)

        print(f"SQL generated in: {OUTPUT_SQL}")

        # Execute BigQuery CLI
        with open(OUTPUT_SQL, "r") as f:
            sql = f.read()

        subprocess.run(
            ["bq", "query", "--use_legacy_sql=false"],
            input=sql,
            text=True,
            check=True
        )
            
    except Exception as e:
        print(f'Error generating sql bigquery tables: {e}')


if __name__ == "__main__":
    create_bigquery_table(SQL_TEMPLATE_DIM)
    create_bigquery_table(SQL_TEMPLATE_FACT)
