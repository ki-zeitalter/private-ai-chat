import {Routes} from '@angular/router';
import {ChatComponent} from "./components/chat/chat.component";
import {PageNotFoundComponent} from "./components/page-not-found/page-not-found.component";

export const routes: Routes = [
  {path: 'chat', component: ChatComponent},
  {path: '', pathMatch: "full", redirectTo: 'chat'},
  {path: '**', component: PageNotFoundComponent}
];
