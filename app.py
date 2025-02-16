from flask import Flask, request, jsonify
from main_v3 import hybrid_recommendation

app = Flask(__name__)


@app.route("/recommendation-class", methods=["GET"])
def recommendation_class():
    user_id = int(request.args.get("user_id"))

    recommendations = hybrid_recommendation(
        user_id=user_id,
        content_weight=0.9,
        collab_weight=0.1,
        top_n=5,
    )

    return jsonify(recommendations.to_dict(orient="records"))


if __name__ == "__main__":
    app.run(debug=True)
