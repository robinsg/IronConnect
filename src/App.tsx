/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect } from 'react';
import { 
  Terminal, 
  Layers, 
  FileCode, 
  Settings, 
  ShieldAlert, 
  Activity, 
  ChevronRight,
  Database,
  Cpu,
  Monitor,
  Folder,
  FileText
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface FrameworkFile {
  name: string;
  type: 'file' | 'directory';
  content?: string;
  path?: string;
  children?: FrameworkFile[];
}

export default function App() {
  const [files, setFiles] = useState<FrameworkFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<FrameworkFile | null>(null);
  const [activeConfig, setActiveConfig] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch('/api/framework/files').then(res => res.json()),
      fetch('/api/framework/config-status').then(res => res.json())
    ])
      .then(([filesData, configData]) => {
        setFiles(filesData);
        setActiveConfig(configData);
        if (filesData.length > 0) {
           // Try to find login_screen.yaml as default
           const findFile = (nodes: FrameworkFile[]): FrameworkFile | null => {
             for (const node of nodes) {
               if (node.name === 'login_screen.yaml') return node;
               if (node.children) {
                 const found = findFile(node.children);
                 if (found) return found;
               }
             }
             return null;
           };
           setSelectedFile(findFile(filesData) || filesData[0]);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching files:', err);
        setLoading(false);
      });
  }, []);

  const renderFileTree = (nodes: FrameworkFile[], depth = 0) => {
    return nodes.map((node) => (
      <div key={node.path || node.name}>
        <button
          onClick={() => node.type === 'file' && setSelectedFile(node)}
          className={cn(
            "flex items-center w-full px-4 py-2 text-[13px] transition-colors",
            "text-[#7D8590] hover:text-[#E6EDF3] hover:bg-[#161B22]",
            selectedFile?.path === node.path && "text-[#E6EDF3] bg-[#161B22] border-l-2 border-[#2F81F7]"
          )}
          style={{ paddingLeft: `${(depth + 1) * 16}px` }}
        >
          {node.type === 'directory' ? <Folder size={14} className="mr-2 opacity-50" /> : <FileText size={14} className="mr-2 opacity-50" />}
          {node.name}
        </button>
        {node.children && renderFileTree(node.children, depth + 1)}
      </div>
    ));
  };

  return (
    <div className="flex flex-col h-screen w-full bg-[#050505] text-[#E6EDF3] overflow-hidden select-none">
      {/* Header */}
      <header className="h-[64px] bg-[#0D0E12] border-b border-[#30363D] flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 border-2 border-[#3FB950] rounded flex items-center justify-center font-extrabold text-[#3FB950]">i</div>
          <div className="text-lg font-semibold tracking-tight">
            IronConnect <span className="text-[#7D8590] font-light">Architect</span>
          </div>
        </div>
        <div className="flex gap-6 text-[11px] text-[#7D8590]">
          <div className="flex flex-col">
            <span className="text-[9px] uppercase tracking-tighter opacity-50">Host</span>
            <span className="text-zinc-300 font-mono">{activeConfig?.host}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[9px] uppercase tracking-tighter opacity-50">Device</span>
            <span className="text-zinc-300 font-mono">{activeConfig?.deviceName || 'AUTO'}</span>
          </div>
          <div className="flex flex-col">
            <span className="text-[9px] uppercase tracking-tighter opacity-50">SSL</span>
            <span className={cn("font-mono", activeConfig?.ssl ? "text-green-500" : "text-yellow-600")}>{activeConfig?.ssl ? 'ENABLED' : 'DISABLED'}</span>
          </div>
          <div className="h-6 w-[1px] bg-zinc-800 self-center"></div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#3FB950] shadow-[0_0_8px_#3FB950]"></span>
            TN5250 ONLINE
          </div>
          <div className="flex flex-col">
             <span className="text-[9px] uppercase tracking-tighter opacity-50">User</span>
             <span className="text-zinc-300 font-mono">{activeConfig?.user}</span>
          </div>
        </div>
      </header>

      {/* Main Grid Layout */}
      <main className="flex-1 grid grid-cols-[260px_1fr_300px] gap-[1px] bg-[#30363D] overflow-hidden">
        {/* Panel 1: Project Explorer */}
        <section className="panel">
          <div className="panel-header">
            <span>Project Explorer</span>
            <Layers size={12} className="opacity-50" />
          </div>
          <div className="flex-1 overflow-y-auto py-2">
            {loading ? (
              <div className="px-6 py-4 text-xs text-[#7D8590] animate-pulse">Scanning framework...</div>
            ) : (
              renderFileTree(files)
            )}
          </div>
          <div className="mt-auto p-4 border-t border-[#30363D]">
            <div className="badge block text-center py-1">PYTHON 3.12.4</div>
          </div>
        </section>

        {/* Panel 2: TN5250 Visual Buffer */}
        <section className="panel border-x border-[#30363D]">
          <div className="panel-header">
            <span>TN5250 Visual Buffer (tmux Capture)</span>
            <span className="text-[#00FF41] font-mono">BUFFER_OK [{activeConfig?.height || 24}x{activeConfig?.width || 80}]</span>
          </div>
          <div className="flex-1 terminal-viewport flex items-center justify-center relative bg-black">
            {/* CRT Overlay Effect */}
            <div className="absolute inset-0 pointer-events-none z-10 opacity-[0.03]" style={{
              backgroundImage: 'linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06))',
              backgroundSize: '100% 2px, 3px 100%'
            }}></div>
            
            <div className="terminal-text font-mono text-sm leading-[1.2] p-10 whitespace-pre">
              {`                                  Sign On

                          System  . . . . . :  ${activeConfig?.host?.toUpperCase() || 'PUB400'}
                          Subsystem . . . . :  QINTER
                          Display . . . . . :  ${activeConfig?.deviceName || 'QPADEV0001'}

            User  . . . . . . . . . . . . .  __________
            Password  . . . . . . . . . . .
            Program/procedure . . . . . . .  __________
            Menu  . . . . . . . . . . . . .  __________
            Current library . . . . . . . .  __________




 (C) COPYRIGHT IBM CORP. 1980, 2024.`}
            </div>
            
            <div className="absolute bottom-4 right-6 bg-[#00FF41] text-black px-1.5 py-0.5 font-bold text-[12px]">X-II</div>
          </div>
        </section>

        {/* Panel 3: Definition / Code */}
        <section className="panel">
          <div className="panel-header">
            <span>{selectedFile?.name.endsWith('.yaml') ? 'YAML Definition' : 'Source Code'}</span>
            <span className="badge">{selectedFile?.name || 'none'}</span>
          </div>
          <div className="flex-1 code-block p-6">
            {selectedFile ? (
              <pre className="whitespace-pre-wrap">
                {selectedFile.content}
              </pre>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-zinc-600">
                <FileCode size={32} className="opacity-20 mb-4" />
                <p className="text-xs">Select file to inspect</p>
              </div>
            )}
          </div>
        </section>
      </main>

      {/* Footer: Logs */}
      <footer className="h-[160px] bg-[#0D0E12] border-t border-[#30363D] flex flex-col shrink-0">
        <div className="panel-header border-b-0">
          <span>Real-time Execution Logs</span>
          <div className="flex gap-4">
             <div className="flex items-center gap-1.5 text-[10px]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#2F81F7]"></span> TRACE
             </div>
             <div className="flex items-center gap-1.5 text-[10px]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#3FB950]"></span> SUCCESS
             </div>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-1 font-mono text-[12px]">
           {[
             { time: '14:20:01', tag: 'INFO', msg: "Initialising libtmux session 'automation_773'..." },
             { time: '14:20:03', tag: 'INFO', msg: "Connecting to IBM i via tn5250 binary (Map: 285)..." },
             { time: '14:20:05', tag: 'STATE', msg: <>Screen detected: <span className="text-white">LOGIN_SCREEN</span> (Verification: 100%)</>, success: true },
             { time: '14:20:06', tag: 'TRACE', msg: "Waiting for Input Inhibited (X-II) to clear..." },
             { time: '14:20:07', tag: 'EXEC', msg: "Sending key sequences for field 'username'...", success: true },
           ].map((log, i) => (
             <div key={i} className="log-entry flex items-start gap-4">
               <span className="text-[#7D8590] shrink-0">{log.time}</span>
               <span className={cn("font-bold shrink-0 w-12", log.success ? 'text-[#3FB950]' : 'text-[#2F81F7]')}>{log.tag}</span>
               <span className="text-[#D1D5DB]">{log.msg}</span>
             </div>
           ))}
        </div>
      </footer>
    </div>
  );
}
