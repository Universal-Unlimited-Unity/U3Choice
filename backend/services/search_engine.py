from sqlalchemy import select, func
from database import eng
from models.user_model import users_table
class SearchEngine:
    def __init__(self, keyword: str):
        self.keyword = keyword
    
    async def SearchForUsers(self, limit: int = 10):
        username_socre = func.similarity(users_table.c.username, self.keyword).label("username_score")
        name_score = func.similarity(users_table.c.name, self.keyword).label("name_score")
        best_score = func.greatest(username_socre, name_score).label("greatest_score")
        
        stmt = select(users_table.c.id, users_table.c.username, 
                    users_table.c.name, users_table.c.photo_url,
                    best_score).where(
                        ((users_table.c.username.op("%")(self.keyword))
                        | 
                        (users_table.c.name.op("%")(self.keyword))), users_table.c.status == "Active").order_by(best_score.desc()).limit(limit)
        with eng.begin() as conn:
            result = conn.execute(stmt).mappings().all()
        return result