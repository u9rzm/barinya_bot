
// Примеры конфигураций
const configs = {
    // Вариант 1: Квадраты
    squares: {
        variant: 'square',
        color: '#B19EEF',
        pixelSize: 4,
        patternDensity: 0.8
    },
    
    // Вариант 2: Круги
    circles: {
        variant: 'circle',
        color: '#4ECDC4',
        pixelSize: 5,
        liquid: true,
        liquidStrength: 0.15
    },
    
    // Вариант 3: Треугольники
    triangles: {
        variant: 'triangle',
        color: '#FF6B6B',
        pixelSize: 6,
        rippleIntensityScale: 1.5
    },
    
    // Вариант 4: Ромбы
    diamonds: {
        variant: 'diamond',
        color: '#96CEB4',
        pixelSize: 4,
        edgeFade: 0.3
    }
};

class PixelBlast {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container with id "${containerId}" not found`);
            return;
        }
        
        // Default options
        this.options = {
            variant: 'square',
            pixelSize: 3,
            color: '#B19EEF',
            patternScale: 2,
            patternDensity: 1,
            liquid: false,
            liquidStrength: 0.1,
            pixelSizeJitter: 0,
            enableRipples: true,
            rippleIntensityScale: 1,
            rippleThickness: 0.1,
            rippleSpeed: 0.3,
            edgeFade: 0.5,
            transparent: true,
            ...options
        };
        
        this.init();
    }
    
    init() {
        // Create canvas and renderer
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: this.options.transparent
        });
        
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        
        if (this.options.transparent) {
            this.renderer.setClearAlpha(0);
        } else {
            this.renderer.setClearColor(0x000000, 1);
        }
        
        this.container.appendChild(this.renderer.domElement);
        
        // Scene and camera
        this.scene = new THREE.Scene();
        this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
        
        // Shader uniforms
        this.uniforms = {
            uResolution: { value: new THREE.Vector2() },
            uTime: { value: 0 },
            uColor: { value: new THREE.Color(this.options.color) },
            uPixelSize: { value: this.options.pixelSize },
            uScale: { value: this.options.patternScale },
            uDensity: { value: this.options.patternDensity },
            uPixelJitter: { value: this.options.pixelSizeJitter },
            uEnableRipples: { value: this.options.enableRipples ? 1 : 0 },
            uRippleSpeed: { value: this.options.rippleSpeed },
            uRippleThickness: { value: this.options.rippleThickness },
            uRippleIntensity: { value: this.options.rippleIntensityScale },
            uEdgeFade: { value: this.options.edgeFade }
        };
        
        // Shape mapping
        const SHAPE_MAP = {
            square: 0,
            circle: 1,
            triangle: 2,
            diamond: 3
        };
        
        this.uniforms.uShapeType = { value: SHAPE_MAP[this.options.variant] || 0 };
        
        // Vertex shader (simple)
        const vertexShader = `
            void main() {
                gl_Position = vec4(position, 1.0);
            }
        `;
        
        // Fragment shader (simplified version)
        const fragmentShader = `
            uniform vec2 uResolution;
            uniform float uTime;
            uniform vec3 uColor;
            uniform float uPixelSize;
            uniform float uScale;
            uniform float uDensity;
            uniform float uPixelJitter;
            uniform int uEnableRipples;
            uniform float uRippleSpeed;
            uniform float uRippleThickness;
            uniform float uRippleIntensity;
            uniform float uEdgeFade;
            uniform int uShapeType;
            
            out vec4 fragColor;
            
            float random(vec2 st) {
                return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
            }
            
            float noise(vec2 p) {
                vec2 ip = floor(p);
                vec2 fp = fract(p);
                float a = random(ip);
                float b = random(ip + vec2(1.0, 0.0));
                float c = random(ip + vec2(0.0, 1.0));
                float d = random(ip + vec2(1.0, 1.0));
                vec2 u = fp * fp * (3.0 - 2.0 * fp);
                return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
            }
            
            void main() {
                vec2 uv = gl_FragCoord.xy / uResolution.xy;
                
                // Pixelation
                vec2 pixelatedUV = floor(uv * uResolution.xy / uPixelSize) * uPixelSize / uResolution.xy;
                
                // Generate pattern
                float pattern = noise(pixelatedUV * uScale + uTime * 0.1);
                pattern = pattern * 0.5 + 0.5;
                
                // Apply density
                float density = uDensity;
                float value = step(density, pattern);
                
                // Apply color
                vec3 finalColor = uColor * value;
                
                // Edge fading
                vec2 edge = smoothstep(0.0, uEdgeFade, uv) * smoothstep(1.0, 1.0 - uEdgeFade, uv);
                float fade = edge.x * edge.y;
                
                // Shape rendering
                vec2 pixelCoord = fract(uv * uResolution.xy / uPixelSize);
                float shape = 0.0;
                
                if (uShapeType == 1) { // Circle
                    shape = step(length(pixelCoord - 0.5), 0.5);
                } else if (uShapeType == 2) { // Triangle
                    shape = step(pixelCoord.y, 1.0 - pixelCoord.x);
                } else if (uShapeType == 3) { // Diamond
                    shape = step(abs(pixelCoord.x - 0.5) + abs(pixelCoord.y - 0.5), 0.5);
                } else { // Square
                    shape = 1.0;
                }
                
                finalColor *= shape * fade;
                fragColor = vec4(finalColor, 1.0);
            }
        `;
        
        // Create material
        this.material = new THREE.ShaderMaterial({
            vertexShader: vertexShader,
            fragmentShader: fragmentShader,
            uniforms: this.uniforms,
            transparent: true,
            depthTest: false,
            depthWrite: false
        });
        
        // Create plane geometry
        const geometry = new THREE.PlaneGeometry(2, 2);
        this.plane = new THREE.Mesh(geometry, this.material);
        this.scene.add(this.plane);
        
        // Set initial resolution
        this.updateResolution();
        
        // Add event listeners
        window.addEventListener('resize', () => this.onResize());
        this.renderer.domElement.addEventListener('click', (e) => this.onClick(e));
        
        // Start animation
        this.clock = new THREE.Clock();
        this.animate();
    }
    
    updateResolution() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        this.renderer.setSize(width, height);
        this.uniforms.uResolution.value.set(width, height);
    }
    
    onResize() {
        this.updateResolution();
    }
    
    onClick(event) {
        if (!this.options.enableRipples) return;
        
        const rect = this.renderer.domElement.getBoundingClientRect();
        const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        
        // You can add ripple effect logic here
        console.log('Click at:', x, y);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        this.uniforms.uTime.value += 0.016; // Approx 60fps
        
        this.renderer.render(this.scene, this.camera);
    }
    
    destroy() {
        window.removeEventListener('resize', () => this.onResize());
        this.container.removeChild(this.renderer.domElement);
        this.renderer.dispose();
    }
}

// Initialize when page loads
window.addEventListener('DOMContentLoaded', () => {
    const pixelBlast = new PixelBlast('canvas-container', {
        variant: 'square',
        color: '#B19EEF',
        pixelSize: 3,
        liquid: false,
        enableRipples: true
    });
    
    // Expose to global scope for control
    window.pixelBlast = pixelBlast;
});