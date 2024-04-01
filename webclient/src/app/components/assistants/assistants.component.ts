import {Component, NgZone, OnInit} from '@angular/core';
import {MatButton, MatMiniFabButton} from "@angular/material/button";
import {MatCard, MatCardActions, MatCardContent, MatCardHeader, MatCardTitle} from "@angular/material/card";
import {NgForOf} from "@angular/common";
import {Assistant} from "../../model/assistant.model";
import {AssistantService} from "../../services/assistant.service";
import {MatIcon} from "@angular/material/icon";
import {RouterLink} from "@angular/router";

@Component({
  selector: 'app-assistants',
  standalone: true,
  imports: [
    MatButton,
    MatCard,
    MatCardActions,
    MatCardContent,
    MatCardHeader,
    MatCardTitle,
    NgForOf,
    MatIcon,
    MatMiniFabButton,
    RouterLink
  ],
  templateUrl: './assistants.component.html',
  styleUrl: './assistants.component.scss'
})
export class AssistantsComponent implements OnInit {

  aiCards: Assistant[] = [];

  constructor(
    private ngZone: NgZone,
    private aiCardService: AssistantService) {
  }

  activate(card: Assistant): void {
    this.aiCardService.activate(card);
  }

  ngOnInit() {
    this.aiCardService.onNewAssistant.subscribe(() => {
      this.ngZone.run(() =>
        window.setTimeout(() => this.loadAssistants(), 2000)
      )

    })

    this.loadAssistants();
  }

  loadAssistants(): void {
    this.aiCardService.getAssistants().subscribe(cards => {
      this.aiCards = cards;
    })
  }


}
