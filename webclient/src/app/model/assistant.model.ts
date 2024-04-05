export interface Assistant {

  assistant_id: string;
  name: string;
  type: string;
  creator: string;
  instructions: string;
  tools: any[];
  description: string;
  provider_id?: string;
  provider?: string;
  files: string[];
}
