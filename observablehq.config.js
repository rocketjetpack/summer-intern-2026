// See https://observablehq.com/framework/config for documentation.
export default {
  // The app’s title; used in the sidebar and webpage titles.
  title: "2026 Summer Network Engineering Internship",

  // The pages and sections in the sidebar. If you don’t specify this option,
  // all pages will be listed in alphabetical order. Listing pages explicitly
  // lets you organize them into sections and have unlisted pages.
  pages: [
    {
      name: "Home", path: "/index"
    },
    {
      name: "Setup",
      open: false,
      pages: [
        { name: "Repo Clone", path: "/week_00/repo" },
        { name: "Workstation", path: "/week_00/workstation" },
        { name: "Lab Servers", path: "/week_00/lab-servers" },
        { name: "Software", path: "/week_00/software" },
      ],
    },
    {
      name: "Tools",
      open: false,
      pages: [
        { name: "Docker Lab", path: "/tools/docker" },
        { name: "Socket Programming", path: "/tools/sockets" },
//        { name: "Podman Lab", path: "/tools/podman" },
      ],
    },
    {
      name: "Week 1: General Info",
      open: false,
      pages: [
        { name: "Objectives", path: "/week_01/objectives"},
        { name: "Personal Notes", path: "/week_01/notes" }
      ],
    },
    {
      name: "Week 2: How a network moves a packet",
      open: false,
      pages: [
        { name: "Objectives", path: "/week_02/objectives" },
        { name: "Resources", path: "/week_02/resources" },
        { name: "Labs", path: "/week_02/code"},
        { name: "Personal Notes", path: "/week_02/notes" }
      ],
    },
    {
      name: "Week 3: Addressing, switching, routing",
      open: false,
      pages: [
        { name: "Objectives", path: "/week_03/objectives" },
        { name: "Resources", path: "/week_03/resources" },
        { name: "Labs", path: "/week_03/code" },
        { name: "Lab 1: L2 Fundamentals", path: "/week_03/lab1" },
        { name: "Lab 2: The L2/L3 Pivot", path: "/week_03/lab2" },
        { name: "Lab 3: Extended Topology", path: "/week_03/lab3" },
        { name: "Code Lab: Subnet Helper", path: "/week_03/subnet-helper" },
        { name: "Code Lab: Path Explorer", path: "/week_03/path-explorer" },
        { name: "Personal Notes", path: "/week_03/notes" }
      ],
    },
    {
      name: "Week 4: TCP, UDP, and congestion",
      open: false,
      pages: [
        { name: "Objectives", path: "/week_04/objectives" },
        { name: "Terminology", path: "/week_04/terminology" },
        { name: "Resources", path: "/week_04/resources" },
        { name: "Labs", path: "/week_04/code"},
        { name: "Lab 0: Build nettools:week04", path: "/week_04/lab0" },
        { name: "Lab 1: Loss × Latency Amplification", path: "/week_04/lab1" },
        { name: "Lab 2: Querying Network Data with the LibreNMS API", path: "/week_04/lab2" },
        { name: "Personal Notes", path: "/week_04/notes" }
      ],
    },
    {
      name: "Week 5: Flow Telemetry — sFlow & NetFlow",
      open: false,
      pages: [
        { name: "Objectives", path: "/week_05/objectives" },
        { name: "Terminology", path: "/week_05/terminology" },
        { name: "Resources", path: "/week_05/resources" },
        { name: "Labs", path: "/week_05/code" },
        { name: "Lab 0: Build nettools:week05", path: "/week_05/lab0" },
        { name: "Lab 1: sFlow — Sampling and Estimation", path: "/week_05/lab1" },
        { name: "Lab 2: NetFlow/IPFIX — Exact Flow Accounting", path: "/week_05/lab2" },
        { name: "Code Lab: Sampling Estimator", path: "/week_05/sampling-estimator" },
        { name: "Personal Notes", path: "/week_05/notes" }
      ],
    },
    {
      name: "Week 6: High-speed Ethernet & optics",
      open: false,
      pages: [
        { name: "Objectives", path: "/week_06/objectives" },
        { name: "Terminology", path: "/week_06/terminology" },
        { name: "Resources", path: "/week_06/resources" },
        { name: "Labs", path: "/week_06/code" },
        { name: "Code Lab: Link Power Budget", path: "/week_06/link-budget" },
        { name: "Personal Notes", path: "/week_06/notes" }
      ],
    },
    {
      name: "Week 7: IPv6 Fundamentals",
      open: false,
      pages: [
        { name: "IPv6 Basics", path: "/week_07/basics" },
        { name: "Terminology", path: "/week_07/terminology" },
        { name: "Resources", path: "/week_07/resources" },
        { name: "Labs", path: "/week_07/code" },
        { name: "Lab 1: IPv6 Addressing & ND", path: "/week_07/lab1" },
        { name: "Code Lab: IPv6 Address Anatomy", path: "/week_07/address-anatomy" },
        { name: "Personal Notes", path: "/week_07/notes" }
      ],
    },
    {
      name: "Week 8: BGP Deep Dive I (Fundamentals & Peering)",
      open: false,
      pages: [
//        { name: "Objectives", path: "/week_08/objectives" },
//        { name: "Resources", path: "/week_08/resources" },
//        { name: "Code Labs", path: "/week_08/code"},
//        { name: "Personal Notes", path: "/week_08/notes" }
      ],
    },
    {
      name: "Week 9: BGP Deep Dive II (Policy, Security & IPv6)",
      open: false,
      pages: [
//        { name: "Objectives", path: "/week_09/objectives" },
//        { name: "Resources", path: "/week_09/resources" },
//        { name: "Code Labs", path: "/week_09/code"},
//        { name: "Personal Notes", path: "/week_09/notes" }
      ],
    },
    {
      name: "Week 10: BGP Production Deployment (Juniper)",
      open: false,
      pages: [
//        { name: "Objectives", path: "/week_10/objectives" },
//        { name: "Resources", path: "/week_10/resources" },
//        { name: "Code Labs", path: "/week_10/code"},
//        { name: "Personal Notes", path: "/week_10/notes" }
      ],
    },
    {
      name: "Stretch Topics",
      open: false,
      pages: [
        { name: "VXLAN: Objectives", path: "/stretch/vxlan/objectives" },
        { name: "VXLAN: Terminology", path: "/stretch/vxlan/terminology" },
        { name: "VXLAN: Resources", path: "/stretch/vxlan/resources" },
        { name: "VXLAN Lab 0: Build nettools:vxlan", path: "/stretch/vxlan/lab0" },
        { name: "VXLAN Lab 1: Flood-and-Learn", path: "/stretch/vxlan/lab1" },
        { name: "VXLAN Code Lab: MTU & Overhead", path: "/stretch/vxlan/vni-overhead" },
        { name: "OSPFv3: Objectives", path: "/stretch/ospfv3/objectives" },
        { name: "OSPFv3: Terminology", path: "/stretch/ospfv3/terminology" },
        { name: "OSPFv3: Resources", path: "/stretch/ospfv3/resources" },
        { name: "OSPFv3 Lab 0: Prepare the FRR Image", path: "/stretch/ospfv3/lab0" },
        { name: "OSPFv3 Lab 1: Dynamic Routing with FRR", path: "/stretch/ospfv3/lab1" },
        { name: "Dual-Stack: Objectives", path: "/stretch/dual-stack/objectives" },
        { name: "Dual-Stack: Terminology", path: "/stretch/dual-stack/terminology" },
        { name: "Dual-Stack Lab 1: Operations & Failure Modes", path: "/stretch/dual-stack/lab1" },
//        { name: "OTN — Transport Between Sites", path: "/stretch/otn" },
//        { name: "InfiniBand & RDMA", path: "/stretch/infiniband" },
//        { name: "Network Security Fundamentals", path: "/stretch/security" },
      ],
    },
  ],

  // Content to add to the head of the page, e.g. for a favicon:
  // The <style> gives every <details> fold-out a light gray background so they
  // stand out from surrounding prose (theme-aware: uses the alt background, so
  // it stays a sensible gray in dark mode too).
  head: '<link rel="icon" href="observable.png" type="image/png" sizes="32x32"><style>details{background-color:var(--theme-background-alt,#f5f5f5);border-radius:6px;padding:0.75rem 1rem;margin:1rem 0;}details summary{cursor:pointer;}</style>',

  // The path to the source root.
  root: "src",

  // Some additional configuration options and their defaults:
  // theme: "default", // try "light", "dark", "slate", etc.
  // header: "", // what to show in the header (HTML)
  // footer: "Built with Observable.", // what to show in the footer (HTML)
  // sidebar: true, // whether to show the sidebar
  // toc: true, // whether to show the table of contents
  // pager: true, // whether to show previous & next links in the footer
  // output: "dist", // path to the output root for build
  // search: true, // activate search
  // linkify: true, // convert URLs in Markdown to links
  // typographer: false, // smart quotes and other typographic improvements
  // preserveExtension: false, // drop .html from URLs
  // preserveIndex: false, // drop /index from URLs
};
