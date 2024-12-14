# Import necessary libraries
import os
# Library to interact with OpenAI API
import openai

# Step 1: Load the API key from the environment variable
# Ensure the API key is retrieved from the environment variable and set for OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    exit()

openai.api_key = api_key

# Step 2: Define the folder containing the images
# Set the folder path where images are stored
image_folder = "/Users/makalliwa/Documents/OM_ODD_diLLMma/3_TestData"

# Step 3: Define the ODD questions
# Create a list of questions to check compliance
odd_questions = [
    "1. Does this image have poor visibility (e.g., heavy rain, snow, fog)?",
    "2. Is the camera obstructed (e.g., by mud, ice, snow)?",
    "3. Is the road in this image a sharp curve?",
    "4. Is the road in this image an on-off ramp?",
    "5. Is the road in this image an intersection?",
    "6. Does the road in this image have restricted lanes?",
    "7. Does the road in this image have construction zones?",
    "8. Is the road in this image highly banked?",
    "9. Is the image affected by bright light (e.g., headlights, sunlight)?",
    "10. Is the road in this image narrow or winding?",
    "11. Is the road in this image on a hill?"
]


# Step 4: Define a function to interact with ChatGPT
# This function creates a prompt and sends it to the GPT model for answers
def ask_chatgpt(image_name, questions):
    # Combine the image name and questions into a single prompt
    prompt = f"The image is from a front-facing camera in a car. Based on this description, answer the following questions with 'yes' or 'no':\n\n"
    prompt += "\n".join(questions)

    # Query OpenAI's API and retrieve the response
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )

    # Split the response text into individual answers
    return response.choices[0].text.strip().split("\n")


# Step 5: Define dictionaries to store results
# compliance_results stores "Compliant" or "Non-compliant" for each image
# compliance_matrix stores detailed answers to each question for each image
compliance_results = {}
compliance_matrix = {}

# Get the list of image files in the folder
image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Step 6: Handle the case where no image files are found
if not image_files:
    print("No image files found in the folder.")
    exit()

# Step 7: Analyze each image in the folder
# Loop through each image file and process it
for image_file in image_files:
    print(f"\nAnalyzing image: {image_file}")

    # Get answers from ChatGPT for the current image
    responses = ask_chatgpt(image_file, odd_questions)

    # Check compliance based on whether all answers are "yes"
    is_compliant = all("yes" in response.lower() for response in responses)

    # Store the compliance results
    compliance_matrix[image_file] = responses
    compliance_results[image_file] = "Compliant" if is_compliant else "Non-compliant"

# Step 8: Output the compliance results
# Print the summary of compliance results for all images
print("\nCompliance Results:")
for photo, compliance in compliance_results.items():
    print(f"{photo}: {compliance}")

# Step 9: Output the compliance matrix
# Print the detailed question-by-question responses for each image
print("\nCompliance Matrix:")
for photo, responses in compliance_matrix.items():
    print(f"{photo}:")
    for question, response in zip(odd_questions, responses):
        print(f"  {question}: {response}")
