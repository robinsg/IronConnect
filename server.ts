import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import fs from 'fs/promises';

async function startServer() {
    const app = express();
    const PORT = 3000;

    // API: Retrieve framework files for the dashboard
    app.get('/api/framework/files', async (req, res) => {
        try {
            const getDirFiles = async (dir: string): Promise<any[]> => {
                const entries = await fs.readdir(path.join(process.cwd(), dir), { withFileTypes: true });
                const files = await Promise.all(entries.map(async (entry) => {
                    const relativePath = path.join(dir, entry.name);
                    if (entry.isDirectory()) {
                        return { name: entry.name, type: 'directory', children: await getDirFiles(relativePath) };
                    }
                    const content = await fs.readFile(path.join(process.cwd(), relativePath), 'utf-8');
                    return { name: entry.name, type: 'file', content, path: relativePath };
                }));
                return files;
            };

            const structure = await getDirFiles('framework');
            res.json(structure);
        } catch (error) {
            res.status(500).json({ error: 'Failed to read framework structure' });
        }
    });

    // API: Retrieve connectivity status (redacted for security)
    app.get('/api/framework/config-status', (req, res) => {
        const deviceType = process.env.IBMI_DEVICE_TYPE || 'IBM-3477-FC';
        const isWide = deviceType.includes('3477');
        res.json({
            host: process.env.IBMI_HOST || 'pub400.com',
            user: process.env.IBMI_USER ? '********' : 'NOT SET',
            password: process.env.IBMI_PASSWORD ? '********' : 'NOT SET',
            ssl: process.env.IBMI_SSL === 'true',
            deviceName: process.env.IBMI_DEVICE_NAME || 'AUTO',
            deviceType: deviceType,
            map: process.env.IBMI_MAP || '285',
            width: isWide ? 132 : 80,
            height: isWide ? 27 : 24
        });
    });

    if (process.env.NODE_ENV !== 'production') {
        const vite = await createViteServer({
            server: { middlewareMode: true },
            appType: 'spa',
        });
        app.use(vite.middlewares);
    } else {
        const distPath = path.join(process.cwd(), 'dist');
        app.use(express.static(distPath));
        app.get('*', (req, res) => {
            res.sendFile(path.join(distPath, 'index.html'));
        });
    }

    app.listen(PORT, '0.0.0.0', () => {
        console.log(`Server running at http://0.0.0.0:${PORT}`);
    });
}

startServer();
