from flask import jsonify, request, send_file
import logging
from db_service import get_latest_trends_data
from video_service import generate_video_prompt, call_video_generation_api

logger = logging.getLogger(__name__)


def register_routes(app):
    """Register all API routes for the application"""

    @app.route('/api/trends', methods=['GET'])
    def get_latest_trends():
        """
        Endpoint to retrieve the most recent trends data from MongoDB
        """
        try:
            latest_trend = get_latest_trends_data()

            if latest_trend is None:
                return jsonify({"error": "Database connection not available"}), 500

            if latest_trend == {}:
                return jsonify({"error": "No trend data available"}), 404

            logger.info(f"Retrieved latest trend data from {latest_trend.get('timestamp', 'unknown timestamp')}")
            return jsonify(latest_trend)

        except Exception as e:
            logger.error(f"Error retrieving trend data: {e}")
            return jsonify({"error": f"Failed to retrieve trend data: {str(e)}"}), 500

    @app.route('/api/generate-video', methods=['POST'])
    def generate_video():
        """
        Endpoint to generate video based on product information and current trends
        """
        try:
            # Get form data from request
            form_data = request.json

            # Validate required fields
            if not form_data or not all(k in form_data for k in ["productName", "description", "scenes"]):
                return jsonify({"error": "Missing required fields"}), 400

            # Get latest trends data
            trends_data = get_latest_trends_data()
            if not trends_data:
                return jsonify({"error": "Could not retrieve trends data"}), 500

            # Generate video prompt using Gemini
            video_prompt = generate_video_prompt(form_data, trends_data)
            if not video_prompt:
                return jsonify({"error": "Failed to generate video prompt"}), 500

            # Extract video generation parameters from form_data if provided
            video_params = {}
            param_keys = ["negative_prompt", "num_inference_steps", "guidance_scale", 
                          "height", "width", "num_frames", "fps"]
            
            for key in param_keys:
                if key in form_data:
                    video_params[key] = form_data[key]

            # Call external video generation API with user parameters
            video_result = call_video_generation_api(video_prompt, **video_params)
            if not video_result:
                return jsonify({"error": "Failed to generate video"}), 500

            logger.info(f"Video generated successfully for {form_data.get('productName')}")
            
            # Handle different response types
            if 'video_path' in video_result:
                # If we received a video file, send it to the client
                video_path = video_result['video_path']
                prompt_for_filename = video_result['prompt'].split('\n')[0] if video_result['prompt'] else "generated_video"
                
                return send_file(
                    video_path, 
                    mimetype='video/mp4', 
                    as_attachment=True,
                    download_name=f"{prompt_for_filename.replace(' ', '_')[:30]}.mp4"
                )
            else:
                # If we received JSON, return it to the client
                return jsonify({
                    "success": True,
                    "videoUrl": video_result.get("json_response", {}).get("videoUrl"),
                    "prompt": video_prompt
                })

        except Exception as e:
            logger.error(f"Error in video generation process: {e}")
            return jsonify({"error": f"Video generation failed: {str(e)}"}), 500
