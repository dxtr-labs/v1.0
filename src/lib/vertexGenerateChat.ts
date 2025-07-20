// /app/lib/vertexgeneratechat.ts
import { GoogleGenAI, HarmCategory, HarmBlockThreshold } from "@google/genai";
import { insertPromptAndResponseToDB } from "./firebase";
import { v4 as uuidv4 } from "uuid";

const ai = new GoogleGenAI({
  vertexai: true,
  project: process.env.GOOGLE_PROJECT_ID!,
  location: "us-central1",
});

const model = "gemini-2.5-flash";

const generationConfig = {
  maxOutputTokens: 65535,
  temperature: 1,
  topP: 1,
  seed: 0,
  safetySettings: [
    { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold: HarmBlockThreshold.BLOCK_NONE },
    { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold: HarmBlockThreshold.BLOCK_NONE },
    { category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold: HarmBlockThreshold.BLOCK_NONE },
    { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_NONE },
  ],
};

const messages: string[] = [
  `You will be connected with a website...`, // msg1Text1
  `**Mapping the Requirements** ...`,       // msg2Text1
  `Okay, this is a fantastic request! ...`, // msg2Text2
  `only send out json file to the database ...`, // msg3Text1
  `**Simplifying Interaction Flow** ...`,        // msg4Text1
  `Okay, I understand. My goal is ...`,          // msg4Text2
  `1) the core purpose is that we are ...`,      // msg5Text1
  `**Designing the Workflow** ...`,              // msg6Text1
  `Okay, this is a fascinating project! ...`,    // msg6Text2
  `ou want to: Connect Vertex AI ...`,           // msg7Text1
  `**Refining Data Input** ...`,                 // msg8Text1
  `Thank you for this detailed overview ...`,    // msg8Text2
  `we can use option b and we are using postgresql in cloudsql`,
  `**Defining Table Schemas** ...`,              // msg10Text1
  `Excellent! PostgreSQL is a great choice ...`, // msg10Text2
  `name whatever u want`,
  `**Designing Database Schemas** ...`,          // msg12Text1
  `Okay, excellent! I appreciate the trust. ...`,// msg12Text2
  `yes`,
  `**Confirming the Details** ...`,              // msg14Text1
  `Fantastic! Thank you for confirming. ...`,    // msg14Text2
  `perfect`,
  `Now generate the final n8n-compatible JSON that accomplishes everything we discussed above. 
   Output ONLY a valid JSON object with:
   - nodes
   - connections
   - parameters
   Do not include commentary. Just output the JSON as a code block.⚠️ Ensure queryParameters are placed directly under parameters, not inside options, for HTTP Request nodes in n8n. Also, avoid double-escaped newlines (\\n) in strings, and always use an existing credential name when referencing credentials.`,
];

export async function runVertexSimulation(user_input: string): Promise<{ response: string; request_id: string }> {
  const chat = ai.chats.create({ model, config: generationConfig });

  let fullText = "";

  for (const prompt of messages) {
    const stream = await chat.sendMessageStream({ message: [{ text: prompt }] });
    for await (const chunk of stream) {
      if (chunk.text) fullText += chunk.text;
    }
  }

  const request_id = uuidv4();
  await insertPromptAndResponseToDB(request_id, user_input, fullText);

  return { response: fullText, request_id };
}
