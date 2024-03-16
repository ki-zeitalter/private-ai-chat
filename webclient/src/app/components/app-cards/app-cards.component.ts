import {Component, OnInit} from '@angular/core';
import {MatButton} from "@angular/material/button";
import {MatCard, MatCardActions, MatCardContent, MatCardHeader, MatCardTitle} from "@angular/material/card";
import {NgForOf} from "@angular/common";
import {AICard} from "../../model/ai-card.model";
import {AiCardService} from "../../services/ai-card.service";

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
    NgForOf
  ],
  templateUrl: './app-cards.component.html',
  styleUrl: './app-cards.component.scss'
})
export class AppCardsComponent implements OnInit {

  aiCards: AICard[] = [];

  constructor(

    private aiCardService: AiCardService) {
  }

  activate(card: AICard): void {
    this.aiCardService.activate(card);
  }

  ngOnInit() {
    this.aiCardService.getAiCards().subscribe(cards => {
      this.aiCards = cards;
    })
  }



}
