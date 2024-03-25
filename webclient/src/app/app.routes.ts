import {Routes} from '@angular/router';
import {ChatComponent} from "./components/chat/chat.component";
import {PageNotFoundComponent} from "./components/page-not-found/page-not-found.component";
import {TextToImageComponent} from "./components/text-to-image/text-to-image.component";
import {AssistantChatComponent} from "./components/assistant-chat/assistant-chat.component";
import {AssistantEditorComponent} from "./components/assistant-editor/assistant-editor.component";

export const routes: Routes = [
  {path: 'chat', component: ChatComponent},
  {path: 'text-to-image', component: TextToImageComponent},
  {path: 'analyzer', component: AssistantChatComponent},
  {path: 'assistant-editor', component: AssistantEditorComponent},
  {path: '', pathMatch: "full", redirectTo: 'chat'},
  {path: '**', component: PageNotFoundComponent}
];
