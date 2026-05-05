import os
from app.services.image.image_generator import image_generator_service
from app.agents.deep_insight_workflow.status import workflow_status

async def image_generator_node(state):
    print("--- IMAGE GENERATOR ---")
    if state.get("safety_blocked"):
        return {
            "image_urls": [],
            "messages": ["Image Generator: skipped by safety policy."],
        }
    final_copy = state["final_copy"]
    output_file = state.get("output_file")
    initial_analysis = state.get("initial_analysis", "")
    image_count = state.get("image_count", 2)
    
    await workflow_status.update_step("image_generator")
    
    image_urls = await image_generator_service.generate_images(final_copy, insight=initial_analysis, image_count=image_count)
    
    if output_file and os.path.exists(output_file) and image_urls:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write("\n\n## 生成的配图\n\n")
            for idx, url in enumerate(image_urls):
                f.write(f"![图片{idx+1}]({url})\n\n")
    
    return {
        "image_urls": image_urls,
        "messages": [f"Image Generator: Generated {len(image_urls)} images."]
    }
