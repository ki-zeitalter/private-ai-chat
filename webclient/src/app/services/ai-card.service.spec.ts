import { TestBed } from '@angular/core/testing';

import { AiCardService } from './ai-card.service';

describe('AiCardService', () => {
  let service: AiCardService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AiCardService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
