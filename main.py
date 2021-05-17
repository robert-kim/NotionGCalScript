import requests


def main():
    with open("database_id.txt") as f:
        database_id = f.readline()
    with open("notion_token.txt") as f:
        notion_token = f.readline()

    #print(database_id)
    #print(notion_token)

if __name__ == '__main__':
    main()

