
document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("uploadForm").addEventListener("submit", function (event) {
        event.preventDefault();
        const fileInput = document.getElementById("file");
        const file = fileInput.files[0];

        const formData = new FormData();
        formData.append('file', file);

        document.getElementById("loading").style.display = "block"; // Show loading sign

        fetch("/process", {
            method: "POST",
            body: formData,
        })
            .then((response) => response.json())
            .then((data) => {
                document.getElementById("loading").style.display = "none"; // Hide loading sign
                document.getElementById("summary").innerHTML = data.result.map(summary => `<li>${summary}</li>`).join("<br>");

                // Display comprehension questions
                const questionsElement = document.getElementById("questions");
                questionsElement.innerHTML = data.questions.map(question => `<li>${question}</li>`).join("<br>");

                // Display solutions
                const solutionsElement = document.getElementById("solutions");
                solutionsElement.innerHTML = data.solutions.map(solution => `<li>${solution}</li>`).join("<br>");

                // Display citations
                const citationsElement = document.getElementById("citations");
                citationsElement.innerHTML = data.citations.map(citation => `<li>${citation}</li>`).join("<br>");
                

                // Show the "Copy All" button
                document.getElementById("copyAllButton").style.display = "block";
            })
            .catch((error) => {
                console.error("Error:", error);
                document.getElementById("loading").style.display = "none"; // Hide loading sign
            });
    });
});

document.getElementById("newSumButton").addEventListener("click", function () {
    // Show the loading sign
    document.getElementById("loading").style.display = "block";

    // Clear the previous summary by setting its content to an empty string
    const summaryElement = document.getElementById("summary");
    summaryElement.innerHTML = "";

    // Make a request to your Flask application's /process endpoint
    fetch("/process", {
        method: "POST",
        body: new FormData(document.getElementById("uploadForm")), // Use the form data
    })
    .then((response) => response.json())
    .then((data) => {
        // Hide the loading sign
        document.getElementById("loading").style.display = "none";

        // Update the content of the #summary element with the new summary
        const summaryElement = document.getElementById("summary");
        summaryElement.innerHTML = data.result.map(summary => `<li>${summary}</li>`).join("<br>");
    })
    .catch((error) => {
        console.error("Error:", error);
        // Hide the loading sign in case of an error
        document.getElementById("loading").style.display = "none";
    });
});

document.getElementById("newQuestionButton").addEventListener("click", function () {
    // Show the loading sign
    document.getElementById("loading").style.display = "block";

    // Clear the previous questions by setting the content of the #questions element to an empty string
    const questionsElement = document.getElementById("questions");
    questionsElement.innerHTML = "";

    // Make a request to your Flask application's /process endpoint
    fetch("/process", {
        method: "POST",
        body: new FormData(document.getElementById("uploadForm")), // Use the form data
    })
    .then((response) => response.json())
    .then((data) => {
        // Hide the loading sign
        document.getElementById("loading").style.display = "none";

        // Update the content of the #questions element with the new questions
        const questionsElement = document.getElementById("questions");
        questionsElement.innerHTML = data.questions.map(question => `<li>${question}</li>`).join("<br>");
    })
    .catch((error) => {
        console.error("Error:", error);
        // Hide the loading sign in case of an error
        document.getElementById("loading").style.display = "none";
    });
});

document.getElementById("newSolButton").addEventListener("click", function () {
    // Show the loading sign
    document.getElementById("loading").style.display = "block";

    // Clear the previous solutions by setting the content of the #solutions element to an empty string
    const solutionsElement = document.getElementById("solutions");
    solutionsElement.innerHTML = "";

    // Make a request to your Flask application's /process endpoint
    fetch("/process", {
        method: "POST",
        body: new FormData(document.getElementById("uploadForm")), // Use the form data
    })
    .then((response) => response.json())
    .then((data) => {
        // Hide the loading sign
        document.getElementById("loading").style.display = "none";

        // Update the content of the #solutions element with the new solutions
        const solutionsElement = document.getElementById("solutions");
        solutionsElement.innerHTML = data.solutions.map(solution => `<li>${solution}</li>`).join("<br>");
    })
    .catch((error) => {
        console.error("Error:", error);
        // Hide the loading sign in case of an error
        document.getElementById("loading").style.display = "none";
    });
});

function copyAllToClipboard() {
    const summaryList = document.getElementById("summary").getElementsByTagName("li");
    const questionsList = document.getElementById("questions").getElementsByTagName("li");
    const solutionsList = document.getElementById("solutions").getElementsByTagName("li");
    const citationsList = document.getElementById("citations").getElementsByTagName("li");

    // Customize which lines to include or exclude
    const filteredSummary = Array.from(summaryList).map(item => `- ${item.textContent}`).filter(line => !line.includes("excludeThis"));
    const filteredQuestions = Array.from(questionsList).map(item => `- ${item.textContent.replace(/\n/g, ' ')}`);
    const filteredSolutions = Array.from(solutionsList).map(item => `- ${item.textContent.replace(/\n/g, ' ')}`);
    const filteredCitations = Array.from(citationsList).map(item => `- ${item.textContent}`);

    // Concatenate the filtered content
    const allText = `Summary:\n${filteredSummary.join('\n')}
                    \n\nQuestions:\n${filteredQuestions.join('\n')}
                    \n\nSolutions:\n${filteredSolutions.join('\n')}
                    \n\nCitations:\n${filteredCitations.join('\n')}`;

    navigator.clipboard.writeText(allText)
        .then(() => {
            alert('Filtered sections copied to clipboard!');
        })
        .catch(err => {
            console.error('Unable to copy to clipboard', err);
        });
}

document.getElementById("submitQuestionButton").addEventListener("click", function () {

    const userQuestion = document.getElementById("userQuestionInput").value;

    const questionsElement = document.getElementById("questions");
    questionsElement.innerHTML += `<li>${userQuestion}</li>`;

    if (!userQuestion) {
        alert("Please enter a question.");
        return;
    }

    // Send the question to the server
    fetch('/submit_question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `question=${encodeURIComponent(userQuestion)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            // Add the solution to the solutions list
            const solutionsElement = document.getElementById("solutions");
            solutionsElement.innerHTML += `<li>${data.answer}</li>`;
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });

    // Clear the input field after submission
    document.getElementById("userQuestionInput").value = '';
});


