import sqlite3

def update_db():
    connection = sqlite3.connect("uknow.db")
    connection.execute("ALTER TABLE uknow_video ADD COLUMN thumbs_up INTEGER")
    connection.execute("ALTER TABLE uknow_video ADD COLUMN top INTEGER")
    connection.execute("ALTER TABLE uknow_video ADD COLUMN has_local_cache INTEGER")
    connection.execute("ALTER TABLE uknow_video ADD COLUMN local_cache_source TEXT")
    connection.execute("update uknow_video set video_type = 'video/'||video_type")



if __name__ == '__main__':
    update_db()