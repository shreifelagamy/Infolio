from models.link_model import Links

def main():
    links = None
    try:
        links = Links()
        print("Links table created successfully!")
    except Exception as e:
        print(f"Error creating links table: {str(e)}")
    finally:
        if links:
            links.close_conn()

if __name__ == "__main__":
    main()
