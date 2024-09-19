document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('problem-form');
    const finalAnswerDiv = document.getElementById('final-answer');
    const copyButton = document.getElementById('copy-button');
    const copyCode = document.getElementById('copy-code');
    
    // Agent output boxes
    const agentOutputs = {
        'Agent1': document.querySelector('#agent-1 .output-box'),
        'Agent2': document.querySelector('#agent-2 .output-box'),
        'Agent3': document.querySelector('#agent-3 .output-box'),
        'Agent4': document.querySelector('#agent-4 .output-box')
    };

    let controller = null; // To control the fetch stream
    let isStreaming = false; // Streaming state

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const userInput = document.getElementById('user_input').value.trim();

        if (!userInput) {
            alert("Please enter a problem description.");
            return;
        }

        // Clear previous outputs
        Object.values(agentOutputs).forEach(outputBox => outputBox.innerHTML = '');
        finalAnswerDiv.innerHTML = '';

        // Initialize AbortController to manage the stream
        controller = new AbortController();
        const signal = controller.signal;
        isStreaming = true;

        // Start the process via fetch
        fetch('/start_process', {
            method: 'POST',
            body: new URLSearchParams({ 'user_input': userInput }),
            signal: signal
        })
        .then(response => {
            if (!response.body) {
                throw new Error("ReadableStream not supported in this browser.");
            }
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            let buffer = '';

            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        isStreaming = false;
                        // Process any remaining buffer data when streaming is done
                        processBuffer(buffer);
                        return;
                    }
                    buffer += decoder.decode(value, { stream: true });
                    processBuffer();
                    read();
                }).catch(error => {
                    if (error.name === 'AbortError') {
                        console.log('Streaming aborted by the user.');
                    } else {
                        console.error('Stream reading error:', error);
                    }
                });
            }

            function processBuffer() {
                const lines = buffer.split('\n\n');
                if (lines.length > 2) {
                    handleFinalAnswer(buffer);
                }
                buffer = lines.pop(); // Last incomplete line
                lines.forEach(line => {
                    if (line.startsWith("data: ")) {
                        const data = line.replace("data: ", "").trim();
                        if (data.startsWith("<strong>")) {
                            handleAgentOutput(data);
                        }
                    }
                });
            }

            read();
        })
        .catch(error => {
            if (error.name !== 'AbortError') {
                console.error('Error:', error);
                finalAnswerDiv.innerHTML += `<span class="text-danger">An error occurred: ${error.message}</span>`;
            }
        });
    });

    function handleAgentOutput(data) {
        const agentMatch = data.match(/<strong>(Agent\d+):<\/strong>/);
        if (agentMatch && agentMatch[1] in agentOutputs) {
            const agentName = agentMatch[1];
            let content = data.replace(/<strong>Agent\d+:<\/strong>/, '').trim();
            content = formatMarkdown(content);
            agentOutputs[agentName].innerHTML += `<p>${content}</p>`;
            agentOutputs[agentName].scrollTop = agentOutputs[agentName].scrollHeight;
        }
    }

    function handleFinalAnswer(data) {
        if (!isStreaming) return;
        finalAnswerDiv.innerHTML = formatMarkdown(data);
    }

    function formatMarkdown(text) {
        text = text.replace(/###\s*(.*)/g, '<strong> $1</strong>');
        text = text.replace(/##\s*(.*)/g, '<h5> $1</h5>');
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        text = text.replace(/\n/g, '<br>');
        return text;
    }
    
    // Copy to Clipboard Functionality
    copyButton.addEventListener('click', function() {
        const text = finalAnswerDiv.innerText;
        navigator.clipboard.writeText(text).then(function() {
            alert('Final Solution copied to clipboard!');
        }, function(err) {
            console.error('Could not copy text: ', err);
        });
    });
    
    copyCode.addEventListener('click', function() {
        const codeBlocks = finalAnswerDiv.querySelectorAll('pre code');
        if (codeBlocks.length === 0) {
            alert(`No code blocks found in output to copy.`);
            return;
        }
        let codeContent = '';
        codeBlocks.forEach(block => {
            codeContent += block.innerText + '\n';
        });
        navigator.clipboard.writeText(codeContent).then(function() {
            alert(`Final code copied to clipboard with proper indentation!`);
        }, function(err) {
            console.error('Could not copy text: ', err);
        });
    });

    // Copy to Clipboard Functionality for Each Agent
    document.querySelectorAll('.copy-agent-button').forEach(button => {
        button.addEventListener('click', function() {
            const agent = this.getAttribute('data-agent');
            const agentNumber = agent.replace('Agent', '');
            const outputBox = document.querySelector(`#agent-${agentNumber} .output-box`);
            const codeBlocks = outputBox.querySelectorAll('pre code');
            if (codeBlocks.length === 0) {
                alert(`No code blocks found in ${agent}'s output to copy.`);
                return;
            }
            let codeContent = '';
            codeBlocks.forEach(block => {
                codeContent += block.innerText + '\n';
            });
            navigator.clipboard.writeText(codeContent).then(function() {
                alert(`${agent}'s code copied to clipboard with proper indentation!`);
            }, function(err) {
                console.error('Could not copy text: ', err);
            });
        });
    });

    // Initialize Bootstrap Modal for Agent Details
    const agentDetailsModal = new bootstrap.Modal(document.getElementById('agentDetailsModal'));
    const modalAgentName = document.getElementById('modal-agent-name');
    const modalAgentContent = document.getElementById('modal-agent-content');
    const modalTitle = document.getElementById('agentDetailsModalLabel');

    const viewDetailButtons = document.querySelectorAll('.view-agent-button');

    viewDetailButtons.forEach(button => {
        button.addEventListener('click', function() {
            const agentIdentifier = this.getAttribute('data-agent');
            const agentNumber = agentIdentifier.replace('Agent', '');
            const agentOutputBox = document.querySelector(`#agent-${agentNumber} .output-box`);
            const agentTitle = document.querySelector(`#agent-${agentNumber} .agent-title`).innerText;
            let agentContent = agentOutputBox.innerHTML.trim() || 'No content available.';
            agentContent = agentContent.replace(/<\/?br\s*\/?>/gi, '<br>');
            agentContent = formatMarkdown(agentContent);
            modalTitle.innerText = `${agentTitle} Details`;
            modalAgentName.innerText = agentTitle;
            modalAgentContent.innerHTML = agentContent;
            agentDetailsModal.show();
        });
    });
});
