import {Component, OnInit} from '@angular/core';
import {MatButton, MatMiniFabButton} from "@angular/material/button";
import {MatCard, MatCardActions, MatCardContent, MatCardHeader, MatCardTitle} from "@angular/material/card";
import {NgForOf} from "@angular/common";
import {Assistant} from "../../model/assistant.model";
import {AssistantService} from "../../services/assistant.service";
import {MatIcon} from "@angular/material/icon";
import {RouterLink} from "@angular/router";

@Component({
  selector: 'app-app-cards',
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
  templateUrl: './app-cards.component.html',
  styleUrl: './app-cards.component.scss'
})
export class AppCardsComponent implements OnInit {

  aiCards: Assistant[] = [];

  constructor(

    private aiCardService: AssistantService) {
  }

  activate(card: Assistant): void {
    this.aiCardService.activate(card);
  }

  ngOnInit() {
    this.aiCardService.getAssistants().subscribe(cards => {
      this.aiCards = cards;
    })
  }



}
