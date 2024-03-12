import {Component, CUSTOM_ELEMENTS_SCHEMA} from '@angular/core';
import {BaseChatComponent} from "../base-chat/base-chat.component";
import {ChatService} from "../../services/chat.service";
import {HighlightModule} from "ngx-highlightjs";
import {CommonModule} from "@angular/common";

@Component({
  selector: 'app-analyzer',
  standalone: true,
  imports: [
    HighlightModule,
    CommonModule,
  ],
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  templateUrl: './analyzer.component.html',
  styleUrl: './analyzer.component.scss'
})
export class AnalyzerComponent extends BaseChatComponent {
  constructor(private _chatService: ChatService) {
    super(_chatService)
  }
}
