import "./Footer.css"

const footerColumns = [
  [
    'CONTACT',
    'CONTRIBUTION GUIDELINES',
    'CODE OF ETHICS',
    'AI POLICY',
    'TERM OF USE',
    'PRIVACY',
    'COMMENT MODERATION',
  ],
  [
    'SUBSCRIBE TO NEWSPAPER',
    'REPRODUCTION COPYRIGHTS',
    'ADVERTISE ON DAWN.COM',
    'BRANDED CONTENT',
    'CAREERS',
    'OBITUARIES',
  ],
  ['PRAYER TIMING', 'STOCK/FOREX/GOLD', 'WEATHER'],
  ['DAWN', 'PRISM', 'IMAGES', 'SPECIAL REPORTS', 'AURORA', 'DAWN NEWS'],
  ['EOS/ICON/YOUNG WORLD', 'CITYFM89', 'HERALD', 'TEELI'],
]

export default function Footer(){
    return(
        <div>
        <footer>
            <img src="/images/footerlogo.png" alt="Dawn footer logo" width="100" />
            <div className="footerlinks">
            {footerColumns.map((column, index) => (
                <div key={index}>
                <ul>
                    {column.map((item) => (
                    <li key={item}>
                        <a href="#">{item}</a>
                    </li>
                    ))}
                </ul>
                </div>
            ))}
            </div>
            <div className="copyright">
            <p>Copyright © 2025, DAWN - Taimour Afzal</p>
            </div>
        </footer>
        </div>
    )
}


