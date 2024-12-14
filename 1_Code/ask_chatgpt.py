import os
import openai  # Library to interact with OpenAI API

# Step 1: Load the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")  # Retrieve the API key from the environment variable
if not api_key:  # Check if the API key is missing
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

openai.api_key = api_key  # Set the API key for OpenAI

# Step 2: Define the folder containing the images
image_folder = "/Users/makalliwa/Documents/OM_ODD_diLLMma/3_TestData"

# Step 3: Define the ODD questions
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

# Step 4: Initialize dictionaries to store results
compliance_results = {}  # To store whether each image is "Compliant" or "Non-compliant"
compliance_matrix = {}  # To store detailed responses for each image and question

# Step 5: Define a function to interact with ChatGPT
def ask_chatgpt(image_name, questions):
    """
    Constructs a prompt using the image name and ODD questions,
    sends it to ChatGPT, and retrieves responses.
    """
    # Create a prompt for ChatGPT
    prompt = f"The image is from a front-facing camera in a car. Based on this description, answer the following questions with 'yes' or 'no':\n\n"
    for question in questions:
        prompt += f"{question}\n"  # Add each question to the prompt

    try:
        # Send the prompt to ChatGPT using OpenAI's API
        response = openai.Completion.create(
            engine="text-davinci-003",  # Specify the GPT model
            prompt=prompt,
            max_tokens=300,  # Limit the length of the response
            temperature=0.7  # Control response creativity (lower = more focused)
        )
        # Split the response into a list of answers
        return response.choices[0].text.strip().split("\n")
    except Exception as e:
        print(f"Error querying ChatGPT: {e}")  # Print an error message if the API call fails
        return ["Error"] * len(questions)  # Return placeholder responses in case of error

# Step 6: Check if the folder exists
if not os.path.exists(image_folder):
    print(f"Error: The folder '{image_folder}' does not exist.")  # Handle missing folder
else:
    # Get the list of image files in the folder
    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

    if not image_files:  # Handle case where no image files are found
        print("No image files found in the folder.")
    else:
        # Step 7: Iterate through each image
        for image_file in image_files:
            print(f"\nAnalyzing image: {image_file}")  # Indicate which image is being processed

            # Ask ChatGPT the ODD questions for the image
            responses = ask_chatgpt(image_file, odd_questions)

            if responses[0] == "Error":  # Skip the image if there's an error
                print(f"Skipping {image_file} due to error in ChatGPT response.")
                continue

            # Determine compliance (all answers must be "yes" to be compliant)
            is_compliant = all("yes" in response.lower() for response in responses)

            # Store results
            compliance_matrix[image_file] = responses  # Detailed responses
            compliance_results[image_file] = "Compliant" if is_compliant else "Non-compliant"  # Compliance status

# Step 8: Output the compliance results
print("\nCompliance Results:")
for photo, compliance in compliance_results.items():
    print(f"{photo}: {compliance}")

# Step 9: Output the compliance matrix
print("\nCompliance Matrix:")
for photo, responses in compliance_matrix.items():
    print(f"{photo}:")  # Print the image name
    for question, response in zip(odd_questions, responses):
        print(f"  {question}: {response}")  # Print each question with its response
