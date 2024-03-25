export interface Assistant {

  agent_id: string;
  name: string;
  type: string;
  creator: string;
  instructions: string;
  tools: any[];
  description: string;
  provider_id?: string;
  provider_name?: string;
  files: string[];
}
