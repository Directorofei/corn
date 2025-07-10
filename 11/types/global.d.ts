// 全局类型声明文件
// 解决 next/server 模块类型问题

declare module "next/server" {
  export interface NextRequest extends Request {
    nextUrl: {
      pathname: string;
      search: string;
      searchParams: URLSearchParams;
    };
    geo?: {
      country?: string;
      region?: string;
      city?: string;
    };
    ip?: string;
    headers: Headers;
    method: string;
    url: string;
    json(): Promise<any>;
    text(): Promise<string>;
    blob(): Promise<Blob>;
    formData(): Promise<FormData>;
  }

  export class NextResponse extends Response {
    static json(body: any, init?: ResponseInit): NextResponse;
    static redirect(url: string | URL, status?: number): NextResponse;
    static rewrite(destination: string | URL): NextResponse;
    static next(): NextResponse;
  }
}

// 解决 Node.js process.env 类型问题
declare namespace NodeJS {
  interface ProcessEnv {
    BACKEND_URL?: string;
    NODE_ENV?: "development" | "production" | "test";
    OPENAI_API_KEY?: string;
    ANTHROPIC_API_KEY?: string;
    GOOGLE_API_KEY?: string;
    JWT_SECRET?: string;
    SESSION_SECRET?: string;
    DATABASE_URL?: string;
    REDIS_URL?: string;
    [key: string]: string | undefined;
  }

  interface Process {
    env: ProcessEnv;
  }
}

declare var process: NodeJS.Process; 