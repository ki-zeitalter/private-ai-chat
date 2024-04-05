import {Component, CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';

import 'deep-chat-dev'
import './code_highlight';
import {MenuComponent} from "./components/menu/menu.component";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    MenuComponent
  ],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {

}
