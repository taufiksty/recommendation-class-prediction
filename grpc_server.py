from concurrent import futures
import grpc
from recommendation_pb2 import Recommendation, RecommendationResponse
from recommendation_pb2_grpc import (
    RecommendationServiceServicer,
    add_RecommendationServiceServicer_to_server,
)
from main_v3 import hybrid_recommendation


class RecommendationService(RecommendationServiceServicer):
    def GetRecommendations(self, request, context):
        user_id = request.user_id
        recommendations_df = hybrid_recommendation(
            user_id=user_id,
            content_weight=0.9,
            collab_weight=0.1,
            top_n=3,
        )

        recommendations = [
            Recommendation(
                id=int(row["id"]) if row["id"] is not None else 0,
                name=str(row["name"]) if row["name"] else "",
                score=(
                    float(row["score"])
                    if isinstance(row["score"], (int, float))
                    else 0.0
                ),
                image=str(row["image"]) if row["image"] else "",
                thumbnail=str(row["thumbnail"]) if row["thumbnail"] else "",
                description=str(row["description"]) if row["description"] else "",
                meta_description=(
                    str(row["meta_description"]) if row["meta_description"] else ""
                ),
                level=str(row["level"]) if row["level"] else "",
                class_category_id=(
                    int(row["class_category_id"])
                    if row["class_category_id"] is not None
                    else 0
                ),
                tags=row["tags"] if isinstance(row["tags"], list) else [],
                slug=str(row["slug"]) if row["slug"] else "",
                method=str(row["method"]) if row["method"] else "",
                media=str(row["media"]) if row["media"] else "",
                prefix_code=str(row["prefix_code"]) if row["prefix_code"] else "",
                materials=str(row["materials"]) if row["materials"] else "",
                collaboration_feed=(
                    str(row["collaboration_feed"]) if row["collaboration_feed"] else ""
                ),
                instructor_id=(
                    int(row["instructor_id"]) if row["instructor_id"] is not None else 0
                ),
                learning_link=str(row["learning_link"]) if row["learning_link"] else "",
                consultancy_link=(
                    str(row["consultancy_link"]) if row["consultancy_link"] else ""
                ),
                consultancy_schedule=(
                    str(row["consultancy_schedule"])
                    if row["consultancy_schedule"]
                    else ""
                ),
                group_chat_link=(
                    str(row["group_chat_link"]) if row["group_chat_link"] else ""
                ),
                price=(
                    float(row["price"])
                    if isinstance(row["price"], (int, float))
                    else 0.0
                ),
                registration_close_date=(
                    str(row["registration_close_date"])
                    if row["registration_close_date"]
                    else ""
                ),
                is_deleted=(
                    bool(row["is_deleted"])
                    if isinstance(row["is_deleted"], (int, str))
                    else False
                ),
                created_at=str(row["created_at"]) if row["created_at"] else "",
                updated_at=str(row["updated_at"]) if row["updated_at"] else "",
                deleted_at=str(row["deleted_at"]) if row["deleted_at"] else "",
            )
            for _, row in recommendations_df.iterrows()
        ]

        return RecommendationResponse(recommendations=recommendations)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_RecommendationServiceServicer_to_server(RecommendationService(), server)
    server.add_insecure_port("[::]:50051")
    print("Python gRPC server running on port 50051...")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
